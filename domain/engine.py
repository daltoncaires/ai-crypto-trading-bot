"""
The core trading engine that orchestrates the trading cycle.
"""
from __future__ import annotations

import time
from datetime import datetime
from typing import TYPE_CHECKING

from utils.load_env import Settings
from utils.logger import get_logger

if TYPE_CHECKING:
    from domain.evaluator import Evaluator
    from domain.ports.data_storage_port import DataStoragePort
    from domain.ports.market_data_port import MarketDataPort
    from domain.strategy import Strategy

logger = get_logger(__name__)


class Engine:
    """
    The trading engine. It orchestrates the evaluator and strategy
    to execute the trading logic.
    """

    def __init__(
        self,
        storage: DataStoragePort,
        market_data: MarketDataPort,
        evaluator: Evaluator,
        strategy: Strategy,
        config: Settings,
        loop_interval: int = 3600,
    ):
        self.storage = storage
        self.market_data = market_data
        self.evaluator = evaluator
        self.strategy = strategy
        self.config = config
        self.loop_interval = loop_interval
        logger.info("Trading Engine initialized.")

    def run(self, run_once: bool = False) -> None:
        """Continuously run trading cycles."""
        logger.info("Starting trading engine...")
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
        """Executes a single trading cycle."""
        coins = self.storage.get_all_coins()
        if not coins:
            logger.warning("No coins found in local storage. Skipping cycle.")
            return

        for coin in coins:
            if not self.evaluator.is_candidate(coin):
                continue

            current_price = self.market_data.get_price_by_coin_id(coin.coin_id)
            if current_price is None:
                logger.warning(f"Unable to fetch price for {coin.symbol}, skipping.")
                continue

            self.storage.update_coin_price_change(coin.symbol, coin.price_change)

            safe_pools = self.evaluator.check_liquidity_pools(coin)
            if not safe_pools:
                logger.debug(f"No safe pools found for {coin.symbol}, skipping buy evaluation.")
            else:
                self.strategy.evaluate_and_execute_buy(coin, current_price, safe_pools)

            self.strategy.evaluate_and_execute_sell(coin, current_price)

            # Record PnL for the portfolio
            self.storage.add_pnl_entry_by_symbol(
                coin.symbol, datetime.now(), current_price
            )
