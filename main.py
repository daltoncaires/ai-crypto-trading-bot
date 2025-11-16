"""Command-line entry point for the trading bot."""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List

from data_access.DAL.coins_DAL import CoinsDAL
from data_access.DAL.orders_DAL import OrdersDAL
from data_access.DAL.portfolio_DAL import PortfolioDAL
from data_access.models.coin import Coin
from services.coingecko_service import CoinGecko
from services.openai_service import OpenAIService
from services.trading_service import TradingService
from utils.load_env import Settings, settings
from workers.initializer import initialize_coin_data
from workers.price_updater import update_coin_prices

BASE_DIR = os.path.dirname(__file__)
COINS_FILE = os.path.join(BASE_DIR, "data_access/data/coins.json")
ORDERS_FILE = os.path.join(BASE_DIR, "data_access/data/orders.json")
PORTFOLIO_FILE = os.path.join(BASE_DIR, "data_access/data/portfolio.json")


@dataclass
class BotDependencies:
    coins_dal: CoinsDAL
    orders_dal: OrdersDAL
    portfolio_dal: PortfolioDAL
    cg: CoinGecko
    ai: OpenAIService


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

    def bootstrap_data(self, refresh_prices: bool = True) -> None:
        """Ensure JSON storage exists and optionally refresh prices."""

        initialize_coin_data(COINS_FILE)
        if refresh_prices:
            update_coin_prices(COINS_FILE)

    def run(self, run_once: bool = False) -> None:
        """Continuously run trading cycles."""

        while True:
            self._run_cycle()
            if run_once:
                break
            print(f"Engine cycle complete, sleeping for {self.loop_interval} seconds.")
            time.sleep(self.loop_interval)

    def _run_cycle(self) -> None:
        coins = self.deps.coins_dal.get_all_coins()
        if not coins:
            print("No coins found in local storage. Skipping cycle.")
            return

        for coin in coins:
            if coin.price_change < self.config.trade.price_change_threshold:
                continue

            current_price = self.deps.cg.get_price_by_coin_id(coin.coin_id)
            if current_price is None:
                print(f"Unable to fetch price for {coin.symbol}, skipping.")
                continue

            self.deps.coins_dal.update_coin_price_change(
                coin.symbol, coin.price_change
            )
            self._handle_buy(coin, current_price)
            self._handle_sell(coin, current_price)
            self.deps.portfolio_dal.add_pnl_entry_by_symbol(
                coin.symbol, datetime.now(), current_price
            )

    def _handle_buy(self, coin: Coin, current_price: float) -> None:
        safe_pools = self._check_pools(coin)
        context = {
            "coin": coin.to_dict(),
            "pools": safe_pools,
            "price_change": coin.price_change,
        }
        recommendation = self.deps.ai.get_chat_completion(
            context, self.config.prompt_template
        )
        if "BUY" not in recommendation.upper():
            print(
                f"NOT buying {coin.symbol} per AI recommendation: {recommendation}"
            )
            return

        print(f"Buying {coin.symbol} per AI recommendation: {recommendation}")
        order = TradingService.buy(
            coin.symbol, current_price, self.config.trade.order_amount
        )

        existing_portfolio = self.deps.portfolio_dal.get_portfolio_item_by_symbol(
            order.symbol
        )
        if existing_portfolio is None:
            self.deps.portfolio_dal.insert_portfolio_item(
                order.symbol, order.buy_price, order.quantity
            )
            print(f"Bought {order.symbol} and inserted new portfolio record.")
        else:
            cost_basis = TradingService.calculate_cost_basis(
                existing_portfolio.cost_basis,
                existing_portfolio.total_quantity,
                order.quantity,
                order.buy_price,
            )
            self.deps.portfolio_dal.update_portfolio_item_by_symbol(
                order.symbol, cost_basis, order.quantity
            )
            print(
                "Bought {symbol}. Updated existing portfolio entry with new order data.".format(
                    symbol=order.symbol
                )
            )

        self.deps.orders_dal.insert_order(
            order.timestamp, order.buy_price, order.quantity, order.symbol, order.direction
        )

    def _handle_sell(self, coin: Coin, current_price: float) -> None:
        buy_orders = self.deps.orders_dal.get_all_orders("BUY")
        filtered_buy_orders = [order for order in buy_orders if order.symbol == coin.symbol]
        if not filtered_buy_orders:
            return

        for order in filtered_buy_orders:
            stop_loss_price = order.buy_price * (1 - self.config.trade.stop_loss / 100)
            take_profit_price = order.buy_price * (1 + self.config.trade.take_profit / 100)
            current_pnl = (current_price - order.buy_price) / order.buy_price * 100

            if current_price <= stop_loss_price or current_price >= take_profit_price:
                sell_order = TradingService.sell(
                    order.symbol, current_price, order.quantity
                )
                trigger = (
                    "Stop Loss" if current_price <= stop_loss_price else "Take Profit"
                )
                print(
                    f"{trigger} Triggered: Sold {order.quantity} of {order.symbol} at ${current_price}"
                )
                self.deps.orders_dal.insert_order(
                    sell_order.timestamp,
                    sell_order.buy_price,
                    sell_order.quantity,
                    sell_order.symbol,
                    sell_order.direction,
                )
                self.deps.coins_dal.update_coin_pnl(order.symbol, current_pnl)

    def _check_pools(self, coin: Coin) -> List[dict]:
        pools_response = self.deps.cg.search_pools(coin.symbol)
        pools_data = pools_response.get("data", []) if isinstance(pools_response, dict) else []
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


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Crypto Trading Bot")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Seconds to sleep between trading cycles (default: 3600).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single trading cycle and exit.",
    )
    parser.add_argument(
        "--skip-refresh",
        action="store_true",
        help="Skip refreshing coin prices during bootstrap.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    deps = BotDependencies(
        coins_dal=CoinsDAL(COINS_FILE),
        orders_dal=OrdersDAL(ORDERS_FILE),
        portfolio_dal=PortfolioDAL(PORTFOLIO_FILE),
        cg=CoinGecko(),
        ai=OpenAIService(),
    )
    bot = TradingBot(deps, settings, loop_interval=args.interval)
    bot.bootstrap_data(refresh_prices=not args.skip_refresh)
    bot.run(run_once=args.once)


if __name__ == "__main__":
    main()

