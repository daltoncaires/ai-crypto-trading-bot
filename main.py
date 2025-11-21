
"""
Main entry point for the AI Crypto Trading Bot.

This script acts as the 'Composition Root' for the application. It initializes
all the adapters (for external services like APIs and databases), injects them
into the core domain logic (the Engine and its components), and starts the
bot's execution cycle.
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

# from dataclasses import replace # No longer needed if not using temp_settings
from domain.plugin_loader import load_plugin  # New import
from infrastructure.adapters.market_data_factory import get_market_data_adapter
from infrastructure.adapters.openai_adapter import OpenAIAdapter
from infrastructure.adapters.storage_factory import get_storage_adapter
from utils.load_env import settings
from utils.logger import get_logger
from workers.tasks import initialize_coin_data_task

logger = get_logger(__name__)


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
        "--init-db",
        action="store_true",
        help="Initializes the database with coin data.",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> None:
    """
    Initializes and runs the trading bot.
    """
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.init_db:
        initialize_coin_data_task.delay()
        print("Database initialization task has been queued.")
        return

    # 1. Initialize Adapters (Infrastructure)
    logger.info("Initializing infrastructure adapters...")
    storage_adapter = get_storage_adapter(settings)

    market_data_adapter = get_market_data_adapter(settings)

    decision_engine_adapter = OpenAIAdapter(settings)

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
        market_data=market_data_adapter,
        config=settings,
    )

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
    except Exception:
        logger.critical("A critical, unhandled error occurred.", exc_info=True)
        sys.exit(1)

