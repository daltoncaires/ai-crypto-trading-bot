"""
Main entry point for the AI Crypto Trading Bot.

This script acts as the 'Composition Root' for the application. It initializes
all the adapters (for external services like APIs and databases), injects them
into the core domain logic (the TradingBot), and starts the bot's execution cycle.
This approach adheres to the Hexagonal Architecture pattern, keeping the core
logic decoupled from the infrastructure.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

from domain.trading_bot import BotDependencies, TradingBot
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
COINS_FILE = os.path.join(BASE_DIR, "data/coins.json")
ORDERS_FILE = os.path.join(BASE_DIR, "data/orders.json")
PORTFOLIO_FILE = os.path.join(BASE_DIR, "data/portfolio.json")


def bootstrap_data(refresh_prices: bool = True) -> None:
    """
    Ensures data stores are initialized and optionally refreshes market data.
    This function is part of the application setup, not core domain logic.
    """
    logger.info("Bootstrapping data...")
    # The workers are tightly coupled to the JSON file structure for now.
    # In a more advanced system, they might also use ports.
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

    # 1. Initialize Adapters (the "Right Side" of the hexagon)
    logger.info("Initializing infrastructure adapters...")
    storage_adapter = JSONStorageAdapter(
        coins_file=COINS_FILE,
        orders_file=ORDERS_FILE,
        portfolio_file=PORTFOLIO_FILE,
    )
    market_data_adapter = CoinGeckoAdapter()
    decision_engine_adapter = OpenAIAdapter()

    # 2. Prepare Dependencies for Injection
    dependencies = BotDependencies(
        storage=storage_adapter,
        market_data=market_data_adapter,
        decision_engine=decision_engine_adapter,
    )

    # 3. Bootstrap application data
    bootstrap_data(refresh_prices=not args.skip_refresh)

    # 4. Initialize and run the Core Domain Logic (the "Hexagon")
    logger.info("Initializing core trading bot domain...")
    bot = TradingBot(dependencies, settings, loop_interval=args.interval)
    bot.run(run_once=args.once)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical("A critical, unhandled error occurred.", exc_info=True)
        sys.exit(1)

