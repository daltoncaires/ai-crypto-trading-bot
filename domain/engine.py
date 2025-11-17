"""
The core trading engine that orchestrates the trading cycle.
"""
from __future__ import annotations

import time
import threading
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from utils.load_env import Settings
from utils.logger import get_logger
from domain.components.engine_component import EngineComponent
from domain.plugin_loader import load_plugin

if TYPE_CHECKING:
    from domain.evaluator import Evaluator
    from domain.ports.data_storage_port import DataStoragePort
    from domain.ports.market_data_port import MarketDataPort
    from domain.strategy import Strategy

logger = get_logger(__name__)


class Engine(EngineComponent):
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
        self.shadow_evaluator: Optional[Evaluator] = None
        self.shadow_strategy: Optional[Strategy] = None

        if self.config.shadow_mode_enabled:
            logger.info("Shadow mode is enabled. Initializing shadow components.")
            try:
                ShadowEvaluatorClass = load_plugin(
                    self.config.shadow_evaluator_module or self.config.evaluator_module,
                    self.config.shadow_evaluator_class or self.config.evaluator_class,
                    self.config.evaluator_version # Use the same version as production by default for shadow
                )
                self.shadow_evaluator = ShadowEvaluatorClass(
                    market_data=self.market_data, config=self.config
                )
                ShadowStrategyClass = load_plugin(
                    self.config.shadow_strategy_module or self.config.strategy_module,
                    self.config.shadow_strategy_class or self.config.strategy_class,
                    self.config.strategy_version # Use the same version as production by default for shadow
                )
                self.shadow_strategy = ShadowStrategyClass(
                    storage=self.storage,
                    decision_engine=self.strategy.decision_engine, # Re-use decision engine
                    config=self.config,
                )
                logger.info("Shadow components initialized successfully.")
            except ImportError as e:
                logger.error(f"Failed to load shadow components: {e}. Disabling shadow mode.")
                self.config.shadow_mode_enabled = False
        
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

            if self.config.shadow_mode_enabled and self.shadow_evaluator and self.shadow_strategy:
                logger.debug(f"Running shadow evaluation for {coin.symbol}...")
                shadow_thread = threading.Thread(
                    target=self._run_shadow_evaluation,
                    args=(coin, current_price),
                    daemon=True # Allow program to exit even if shadow thread is running
                )
                shadow_thread.start()

    def _run_shadow_evaluation(self, coin: Coin, current_price: float) -> None:
        """Executes the shadow evaluation logic for a single coin."""
        try:
            shadow_is_candidate = self.shadow_evaluator.is_candidate(coin)
            logger.info(f"[SHADOW] {coin.symbol} - is_candidate: {shadow_is_candidate}")

            if not shadow_is_candidate:
                return

            shadow_safe_pools = self.shadow_evaluator.check_liquidity_pools(coin)
            logger.info(f"[SHADOW] {coin.symbol} - safe_pools count: {len(shadow_safe_pools)}")

            if shadow_safe_pools:
                # Note: Shadow strategy's buy/sell methods should ideally not
                # perform actual trades or modify storage in a real shadow environment.
                # For this example, we'll just log the intent.
                self.shadow_strategy.evaluate_and_execute_buy(coin, current_price, shadow_safe_pools)
            else:
                logger.info(f"[SHADOW] {coin.symbol} - No safe pools found for buy evaluation.")

            self.shadow_strategy.evaluate_and_execute_sell(coin, current_price)

        except Exception as e:
            logger.error(f"[SHADOW] Error during shadow evaluation for {coin.symbol}: {e}", exc_info=True)

