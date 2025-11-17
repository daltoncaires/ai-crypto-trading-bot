"""Utility script that replays historical data through the AI prompt."""

import os
import sys
from typing import List

from data_access.DAL.coins_DAL import CoinsDAL
from services.coingecko_service import CoinGecko
from services.openai_service import OpenAIService
from utils.load_env import settings
from utils.logger import get_logger

logger = get_logger(__name__)

COINS_FILE = os.path.join(os.path.dirname(__file__), "data_access/data/coins.json")

coins_dal = CoinsDAL(COINS_FILE)
ai = OpenAIService()
cg = CoinGecko()


def run_backtest_single_coin(
    symbol: str, prompt_template: str = settings.prompt_template
):
    coin = coins_dal.get_coin_by_symbol(symbol)
    if not coin:
        logger.error(f"Coin with symbol '{symbol}' not found.")
        return [], []

    results: List[dict] = []
    buy_entries: List[dict] = []
    logger.info(f"Running backtest for {symbol} with {len(coin.prices)} data points...")
    for i, price_entry in enumerate(coin.prices, start=1):
        price_slice = coin.prices[:i]
        timestamp = price_entry[0]
        close = price_entry[-1]

        recommendation = ai.get_chat_completion(price_slice, prompt_template)
        logger.debug(f"Recommendation for timestamp {timestamp}: {recommendation}")
        if "BUY" in recommendation.upper():
            buy_entries.append({"timestamp": timestamp, "buy_price": close})
        results.append(
            {
                "symbol": coin.symbol,
                "timestamp": timestamp,
                "close": close,
                "recommendation": recommendation,
            }
        )
    # Calculate PNL for each buy entry using the final price in the price list
    final_price = coin.prices[-1][-1] if coin.prices else None
    for entry in buy_entries:
        entry["final_price"] = final_price
        entry["pnl"] = (
            (final_price - entry["buy_price"]) / entry["buy_price"] * 100
            if final_price is not None
            else None
        )
    return results, buy_entries


if __name__ == "__main__":
    try:
        symbol = input("Enter coin symbol to backtest: ").strip()
        if not symbol:
            logger.warning("No symbol entered. Exiting.")
            sys.exit(0)

        results, buy_entries = run_backtest_single_coin(symbol)

        logger.info("\n--- All Recommendations ---")
        for r in results:
            logger.info(r)

        logger.info("\n--- Buy Signals and PNL ---")
        if not buy_entries:
            logger.info("No buy signals were generated.")
        for b in buy_entries:
            logger.info(b)

    except Exception as e:
        logger.critical("An unexpected error occurred during backtest.", exc_info=True)
        sys.exit(1)
