from typing import List

from celery import shared_task
from domain.models.coin import Coin
from infrastructure.adapters.market_data_factory import get_market_data_adapter
from infrastructure.adapters.storage_factory import get_storage_adapter
from utils.load_env import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@shared_task
def initialize_coin_data_task():
    """
    Ensures the coin data store exists and populates it with initial data
    from the market data source if it's empty.
    """
    logger.info("Initializing coin data store...")
    storage = get_storage_adapter(settings)

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


@shared_task
def update_coin_prices_task() -> List[Coin]:
    """
    Updates the local coin data store with the latest market data.
    """
    logger.info("Starting coin price update process...")
    storage = get_storage_adapter(settings)
    market_data = get_market_data_adapter(settings)

    local_coins = storage.get_all_coins()
    local_coin_ids = {c.coin_id for c in local_coins}

    if not local_coins:
        logger.warning("There are no coins in the data store, cannot update prices.")
        return []

    logger.info(f"Fetching latest market data from {settings.market_data_provider}...")
    latest_coins = market_data.get_coins()
    new_coins_count = 0

    for coin in latest_coins:
        if coin.coin_id not in local_coin_ids:
            new_coins_count += 1
            storage.add_coin(coin.symbol, coin.coin_id)
            ohlc_data = market_data.get_historic_ohlc_by_coin_id(coin.coin_id, days=1)
            storage.add_prices_to_coin(coin.symbol, ohlc_data)
        else:
            if coin.prices:
                storage.add_prices_to_coin(coin.symbol, coin.prices)
            storage.update_coin_price_change(coin.symbol, coin.price_change)

    logger.info(f"Price data updated for {len(latest_coins)} coins.")
    if new_coins_count > 0:
        logger.info(
            f"Inserted {new_coins_count} new coins into the data store "
            "due to market cap changes."
        )
    return latest_coins
