import os
from data_access.DAL.coins_DAL import CoinsDAL
from services.coingecko_service import CoinGecko
from utils.logger import get_logger

logger = get_logger(__name__)


def initialize_coin_data(coins_file):
    # Ensure coins.json exists
    logger.info(f"Initializing coin data store at {coins_file}...")
    if not os.path.exists(coins_file):
        with open(coins_file, "w") as f:
            f.write("[]")
    coins_dal = CoinsDAL(coins_file)
    if len(coins_dal.get_all_coins()) > 0:
        logger.info("Coin data store is already initialized, skipping.")
        return

    logger.info("Fetching initial coin list from CoinGecko...")
    cg = CoinGecko()
    all_coins = cg.get_coins()

    for coin in all_coins:
        logger.debug(f"Adding initial data for {coin.symbol}")
        coins_dal.add_coin(coin.symbol, coin.coin_id)

        ohlc_data = cg.get_historic_ohlc_by_coin_id(
            coin.coin_id, days=1, interval="hourly"
        )
        coins_dal.add_prices_to_coin(coin.symbol, ohlc_data)

    logger.info(f"Added {len(all_coins)} coins to the data store.")
    logger.info(f"Added historical prices to {len(all_coins)} coins.")
