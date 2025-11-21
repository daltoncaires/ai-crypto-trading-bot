"""
Encapsulates the trading strategy logic.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from domain.components.strategy_component import StrategyComponent
from domain.models.coin import Coin
from domain.technical_analysis import calculate_rsi
from domain.trading_service import TradingService
from utils.load_env import Settings
from utils.logger import get_logger

if TYPE_CHECKING:
    from domain.ports.data_storage_port import DataStoragePort
    from domain.ports.decision_engine_port import DecisionEnginePort
    from domain.ports.market_data_port import MarketDataPort


logger = get_logger(__name__)


class StrategyV1(StrategyComponent):
    """
    Contains the logic for making buy or sell decisions based on market
    data and AI recommendations. This is version 1.
    """

    def __init__(
        self,
        storage: DataStoragePort,
        decision_engine: DecisionEnginePort,
        market_data: MarketDataPort,
        config: Settings,
    ):
        self.storage = storage
        self.decision_engine = decision_engine
        self.market_data = market_data
        self.config = config
        logger.info("StrategyV1 component initialized.")

    def evaluate_and_execute_buy(self, coin: Coin, current_price: float, safe_pools: list):
        """Evaluates and executes a buy order if the strategy conditions are met."""
        # NOTE: This assumes that historical data is fetched and available.
        # The application's main loop or data provider needs to ensure this.
        historical_data = self.market_data.get_historical_data(
            coin.symbol, "1d", limit=100
        )
        if historical_data.empty:
            logger.warning(f"Not enough historical data for {coin.symbol} to calculate RSI.")
            return

        close_prices = pd.Series(historical_data["close"])
        rsi = calculate_rsi(close_prices)
        current_rsi = rsi.iloc[-1] if not rsi.empty else None

        context = {
            "coin": coin.to_dict(),
            "pools": safe_pools,
            "price_change": coin.price_change,
            "rsi": current_rsi,
        }
        recommendation = self.decision_engine.get_chat_completion(
            context, self.config.prompt_template
        )

        decision = "NEUTRAL/SELL"
        if "BUY" in recommendation.upper():
            decision = "BUY"

        log_extra = {
            "symbol": coin.symbol,
            "decision": decision,
            "reason": recommendation,
            "price": current_price,
            "rsi": current_rsi,
        }

        if decision != "BUY":
            logger.info(f"AI recommendation for {coin.symbol}: {decision}", extra=log_extra)
            return

        logger.info(f"AI recommendation for {coin.symbol}: {decision}", extra=log_extra)
        order = TradingService.buy(
            coin.symbol, current_price, self.config.trade.order_amount
        )

        buy_log_extra = {
            "symbol": order.symbol,
            "decision": "EXECUTE_BUY",
            "reason": "AI_RECOMMENDATION",
            "price": order.buy_price,
            "quantity": order.quantity,
        }
        logger.info(f"Executed BUY for {order.symbol}", extra=buy_log_extra)

        existing_portfolio = self.storage.get_portfolio_item_by_symbol(order.symbol)
        if existing_portfolio is None:
            self.storage.insert_portfolio_item(
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
            self.storage.update_portfolio_item_by_symbol(
                order.symbol, cost_basis, order.quantity
            )
            logger.info(
                f"Bought {order.symbol}. Updated portfolio with new order data."
            )

        self.storage.insert_order(
            order.timestamp,
            order.buy_price,
            order.quantity,
            order.symbol,
            order.direction,
        )

    def evaluate_and_execute_sell(self, coin: Coin, current_price: float):
        """Evaluates and executes a sell order if the strategy conditions are met."""
        buy_orders = self.storage.get_all_orders("BUY")
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
                trigger = (
                    "STOP_LOSS" if current_price <= stop_loss_price else "TAKE_PROFIT"
                )
                
                sell_log_extra = {
                    "symbol": order.symbol,
                    "decision": "EXECUTE_SELL",
                    "reason": trigger,
                    "price": current_price,
                    "quantity": order.quantity,
                    "pnl_percentage": current_pnl,
                }
                logger.info(
                    f"{trigger} Triggered: Selling {order.quantity} of {order.symbol}",
                    extra=sell_log_extra,
                )

                sell_order = TradingService.sell(
                    order.symbol, current_price, order.quantity
                )
                self.storage.insert_order(
                    sell_order.timestamp,
                    sell_order.buy_price,
                    sell_order.quantity,
                    sell_order.symbol,
                    sell_order.direction,
                )
                self.storage.update_coin_pnl(order.symbol, current_pnl)
