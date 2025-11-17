"""
Encapsulates the trading strategy logic.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List

from domain.models.coin import Coin
from domain.trading_service import TradingService
from utils.load_env import Settings
from utils.logger import get_logger
from domain.components.strategy_component import StrategyComponent

if TYPE_CHECKING:
    from domain.ports.data_storage_port import DataStoragePort
    from domain.ports.decision_engine_port import DecisionEnginePort

logger = get_logger(__name__)


class StrategyV2(StrategyComponent):
    """
    Contains the logic for making buy or sell decisions based on market
    data and AI recommendations. This is version 2, with a slightly
    modified buy evaluation.
    """

    def __init__(
        self,
        storage: DataStoragePort,
        decision_engine: DecisionEnginePort,
        config: Settings,
    ):
        self.storage = storage
        self.decision_engine = decision_engine
        self.config = config
        logger.info("StrategyV2 component initialized.")

    def evaluate_and_execute_buy(self, coin: Coin, current_price: float, safe_pools: list):
        """Evaluates and executes a buy order if the strategy conditions are met."""
        logger.info(f"StrategyV2: Running evaluate_and_execute_buy for {coin.symbol}")
        context = {
            "coin": coin.to_dict(),
            "pools": safe_pools,
            "price_change": coin.price_change,
        }
        recommendation = self.decision_engine.get_chat_completion(
            context, self.config.prompt_template
        )

        # V2 modification: Only buy if recommendation is strong BUY
        if "STRONG BUY" not in recommendation.upper():
            logger.info(
                f"AI recommendation for {coin.symbol}: Not a STRONG BUY (V2). Details: {recommendation}"
            )
            return

        logger.info(f"AI recommendation for {coin.symbol}: STRONG BUY (V2). Details: {recommendation}")
        order = TradingService.buy(
            coin.symbol, current_price, self.config.trade.order_amount
        )

        existing_portfolio = self.storage.get_portfolio_item_by_symbol(order.symbol)
        if existing_portfolio is None:
            self.storage.insert_portfolio_item(
                order.symbol, order.buy_price, order.quantity
            )
            logger.info(f"Bought {order.symbol} and inserted new portfolio record (V2).")
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
                f"Bought {order.symbol}. Updated portfolio with new order data (V2)."
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
                sell_order = TradingService.sell(
                    order.symbol, current_price, order.quantity
                )
                trigger = (
                    "Stop Loss" if current_price <= stop_loss_price else "Take Profit"
                )
                logger.info(
                    f"{trigger} Triggered: Sold {order.quantity} of {order.symbol} at ${current_price} (V2)"
                )
                self.storage.insert_order(
                    sell_order.timestamp,
                    sell_order.buy_price,
                    sell_order.quantity,
                    sell_order.symbol,
                    sell_order.direction,
                )
                self.storage.update_coin_pnl(order.symbol, current_pnl)
