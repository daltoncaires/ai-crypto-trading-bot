import os

from infrastructure.adapters.market_data_factory import get_market_data_adapter
from infrastructure.adapters.json_storage_adapter import JSONStorageAdapter
from utils.logger import get_logger
from utils.load_env import settings

logger = get_logger(__name__)


def initialize_coin_data(coins_file: str):
    """
    Ensures the coin data store exists and populates it with initial data
    from the market data source if it's empty.
    """
    logger.info(f"Initializing coin data store at {coins_file}...")
    if not os.path.exists(coins_file):
        with open(coins_file, "w") as f:
            f.write("[]")

    # The initializer needs a specialized storage adapter for this task.
    # We assume the portfolio and orders files are not needed here.
    storage = JSONStorageAdapter(
        coins_file=coins_file, orders_file="", portfolio_file=""
    )

    if len(storage.get_all_coins()) > 0:
        logger.info("Coin data store is already initialized, skipping.")
        return

    logger.info(f"Fetching initial coin list from {settings.market_data_provider}...")
    market_data = get_market_data_adapter(settings)
    all_coins = market_data.get_coins()

    for coin in all_coins:
        logger.debug(f"Adding initial data for {coin.symbol}")
        storage.add_coin(coin.symbol, coin.coin_id)

        ohlc_data = market_data.get_historic_ohlc_by_coin_id(
            coin.coin_id, days=1, interval="hourly"
        )
        storage.add_prices_to_coin(coin.symbol, ohlc_data)

    logger.info(f"Added {len(all_coins)} coins to the data store.")
    logger.info(f"Added historical prices to {len(all_coins)} coins.")
