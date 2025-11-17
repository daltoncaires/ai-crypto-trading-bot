from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import List

from domain.models.coin import Coin
from domain.ports.data_storage_port import DataStoragePort
from domain.ports.decision_engine_port import DecisionEnginePort
from domain.ports.market_data_port import MarketDataPort
from domain.trading_service import TradingService
from utils.load_env import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BotDependencies:
    """Dependencies required by the TradingBot, using Ports."""

    storage: DataStoragePort
    market_data: MarketDataPort
    decision_engine: DecisionEnginePort


class TradingBot:
    """High-level orchestrator that ties DALs and services together."""

    def __init__(
        self,
        deps: BotDependencies,
        config: Settings,
        loop_interval: int = 3600,
    ) -> None:
        self.deps = deps
        self.config = config
        self.loop_interval = loop_interval

    def run(self, run_once: bool = False) -> None:
        """Continuously run trading cycles."""
        logger.info("Starting trading bot...")
        while True:
            logger.info("Starting new trading cycle.")
            self._run_cycle()
            if run_once:
                logger.info("Run-once flag is set, shutting down.")
                break
            logger.info(
                f"Engine cycle complete, sleeping for {self.loop_interval} seconds."
            )
            time.sleep(self.loop_interval)

    def _run_cycle(self) -> None:
        coins = self.deps.storage.get_all_coins()
        if not coins:
            logger.warning("No coins found in local storage. Skipping cycle.")
            return

        for coin in coins:
            if coin.price_change < self.config.trade.price_change_threshold:
                logger.debug(
                    f"Skipping {coin.symbol} due to low price change: "
                    f"{coin.price_change} < {self.config.trade.price_change_threshold}"
                )
                continue

            current_price = self.deps.market_data.get_price_by_coin_id(coin.coin_id)
            if current_price is None:
                logger.warning(f"Unable to fetch price for {coin.symbol}, skipping.")
                continue

            self.deps.storage.update_coin_price_change(
                coin.symbol, coin.price_change
            )
            self._handle_buy(coin, current_price)
            self._handle_sell(coin, current_price)
            self.deps.storage.add_pnl_entry_by_symbol(
                coin.symbol, datetime.now(), current_price
            )

    def _handle_buy(self, coin: Coin, current_price: float) -> None:
        safe_pools = self._check_pools(coin)
        context = {
            "coin": coin.to_dict(),
            "pools": safe_pools,
            "price_change": coin.price_change,
        }
        recommendation = self.deps.decision_engine.get_chat_completion(
            context, self.config.prompt_template
        )
        if "BUY" not in recommendation.upper():
            logger.info(
                f"AI recommendation for {coin.symbol}: NEUTRAL/SELL. Details: {recommendation}"
            )
            return

        logger.info(f"AI recommendation for {coin.symbol}: BUY. Details: {recommendation}")
        order = TradingService.buy(
            coin.symbol, current_price, self.config.trade.order_amount
        )

        existing_portfolio = self.deps.storage.get_portfolio_item_by_symbol(
            order.symbol
        )
        if existing_portfolio is None:
            self.deps.storage.insert_portfolio_item(
                order.symbol, order.buy_price, order.quantity
            )
            logger.info(f"Bought {order.symbol} and inserted new portfolio record.")
        else:
            cost_basis = TradingService.calculate_cost_basis(
                existing_portfolio.cost_basis,
                existing_portfolio.total_quantity,
                order.quantity,
                order.buy_price,
            )
            self.deps.storage.update_portfolio_item_by_symbol(
                order.symbol, cost_basis, order.quantity
            )
            logger.info(
                f"Bought {order.symbol}. Updated existing portfolio entry with new order data."
            )

        self.deps.storage.insert_order(
            order.timestamp,
            order.buy_price,
            order.quantity,
            order.symbol,
            order.direction,
        )

    def _handle_sell(self, coin: Coin, current_price: float) -> None:
        buy_orders = self.deps.storage.get_all_orders("BUY")
        filtered_buy_orders = [
            order for order in buy_orders if order.symbol == coin.symbol
        ]
        if not filtered_buy_orders:
            return

        for order in filtered_buy_orders:
            stop_loss_price = order.buy_price * (1 - self.config.trade.stop_loss / 100)
            take_profit_price = order.buy_price * (
                1 + self.config.trade.take_profit / 100
            )
            current_pnl = (current_price - order.buy_price) / order.buy_price * 100

            if current_price <= stop_loss_price or current_price >= take_profit_price:
                sell_order = TradingService.sell(
                    order.symbol, current_price, order.quantity
                )
                trigger = (
                    "Stop Loss" if current_price <= stop_loss_price else "Take Profit"
                )
                logger.info(
                    f"{trigger} Triggered: Sold {order.quantity} of {order.symbol} at ${current_price}"
                )
                self.deps.storage.insert_order(
                    sell_order.timestamp,
                    sell_order.buy_price,
                    sell_order.quantity,
                    sell_order.symbol,
                    sell_order.direction,
                )
                self.deps.storage.update_coin_pnl(order.symbol, current_pnl)

    def _check_pools(self, coin: Coin) -> List[dict]:
        pools_response = self.deps.market_data.search_pools(coin.symbol)
        pools_data = (
            pools_response.get("data", []) if isinstance(pools_response, dict) else []
        )
        filtered_pools = []
        for pool in pools_data:
            reserve = pool.get("reserve_in_usd", 0)
            volume = pool.get("volume_in_usd", {}).get("h24", 0)
            buys = pool.get("buys_24h", 0)
            if (
                reserve >= self.config.pool.min_reserves_usd
                and volume >= self.config.pool.min_volume_24h
                and buys >= self.config.pool.min_buys_24h
            ):
                filtered_pools.append(pool)
        return filtered_pools
