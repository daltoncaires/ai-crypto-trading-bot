from typing import List

from domain.models.coin import Coin
from domain.ports.market_data_port import MarketDataPort
from infrastructure.adapters.json_storage_adapter import JSONStorageAdapter
from infrastructure.adapters.market_data_factory import get_market_data_adapter
from utils.logger import get_logger
from utils.load_env import settings # Import settings

logger = get_logger(__name__)


def _fetch_and_add_historic_prices(
    storage: JSONStorageAdapter, symbol: str, ohlc_data: List[list]
):
    prices = []
    for candle in ohlc_data:
        timestamp = int(candle[0]) / 1000  # Convert ms to s
        prices.append(
            [timestamp, candle[1], candle[2], candle[3], candle[4]]  # O, H, L, C
        )
    storage.add_prices_to_coin(symbol, prices)


def _add_new_coin_with_history(
    storage: JSONStorageAdapter,
    market_data: MarketDataPort,
    symbol: str,
    coin_id: str,
):
    logger.info(f"New coin '{symbol}' found. Fetching its historical data.")
    storage.add_coin(symbol, coin_id)
    ohlc_data = market_data.get_historic_ohlc_by_coin_id(coin_id, days=1)
    _fetch_and_add_historic_prices(storage, symbol, ohlc_data)


def update_coin_prices(coins_file: str) -> List[Coin]:
    """
    Updates the local coin data store with the latest market data.
    """
    logger.info("Starting coin price update process...")
    # This worker also needs its own adapter instances.
    storage = JSONStorageAdapter(coins_file=coins_file, orders_file="", portfolio_file="")
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
            _add_new_coin_with_history(
                storage, market_data, coin.symbol, coin.coin_id
            )
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
