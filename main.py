"""
Main entry point for the AI Crypto Trading Bot.

This script acts as the 'Composition Root' for the application. It initializes
all the adapters (for external services like APIs and databases), injects them
into the core domain logic (the Engine and its components), and starts the
bot's execution cycle.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

# from dataclasses import replace # No longer needed if not using temp_settings
from domain.plugin_loader import load_plugin # New import
# Removed direct imports of Engine, Evaluator, Strategy
from infrastructure.adapters.coingecko_adapter import CoinGeckoAdapter
from infrastructure.adapters.json_storage_adapter import JSONStorageAdapter
from infrastructure.adapters.openai_adapter import OpenAIAdapter
from utils.load_env import settings
from utils.logger import get_logger
from workers.initializer import initialize_coin_data
from workers.price_updater import update_coin_prices

logger = get_logger(__name__)

# --- File Paths for JSON Storage Adapter ---
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
COINS_FILE = os.path.join(DATA_DIR, "coins.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "portfolio.json")


def bootstrap_data(refresh_prices: bool = True) -> None:
    """
    Ensures data stores are initialized and optionally refreshes market data.
    """
    logger.info("Bootstrapping data...")
    os.makedirs(DATA_DIR, exist_ok=True)
    initialize_coin_data(COINS_FILE)
    if refresh_prices:
        update_coin_prices(COINS_FILE)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Parses command-line arguments."""
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
    """
    Initializes and runs the trading bot.
    """
    args = parse_args(argv if argv is not None else sys.argv[1:])

    # 1. Initialize Adapters (Infrastructure)
    logger.info("Initializing infrastructure adapters...")
    storage_adapter = JSONStorageAdapter(
        coins_file=COINS_FILE,
        orders_file=ORDERS_FILE,
        portfolio_file=PORTFOLIO_FILE,
    )
    market_data_adapter = CoinGeckoAdapter()
    decision_engine_adapter = OpenAIAdapter()

    # 2. Initialize Domain Components
    logger.info("Initializing core domain components...")

    # Dynamically load Evaluator
    EvaluatorClass = load_plugin(
        settings.evaluator_module, settings.evaluator_class, settings.evaluator_version
    )
    evaluator = EvaluatorClass(market_data=market_data_adapter, config=settings)

    # Dynamically load Strategy
    StrategyClass = load_plugin(
        settings.strategy_module, settings.strategy_class, settings.strategy_version
    )
    strategy = StrategyClass(
        storage=storage_adapter,
        decision_engine=decision_engine_adapter,
        config=settings,
    )

    # 3. Bootstrap application data
    bootstrap_data(refresh_prices=not args.skip_refresh)

    # 4. Initialize and run the Core Trading Engine
    logger.info("Initializing core trading engine...")
    # Dynamically load Engine
    EngineClass = load_plugin(settings.engine_module, settings.engine_class)
    engine = EngineClass(
        storage=storage_adapter,
        market_data=market_data_adapter,
        evaluator=evaluator,
        strategy=strategy,
        config=settings,
        loop_interval=args.interval,
    )
    engine.run(run_once=args.once)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical("A critical, unhandled error occurred.", exc_info=True)
        sys.exit(1)

