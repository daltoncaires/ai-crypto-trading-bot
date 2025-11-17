import os
from typing import List
from data_access.DAL.coins_DAL import CoinsDAL
from data_access.models.coin import Coin
from services.coingecko_service import CoinGecko
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


def fetch_and_add_historic_prices(symbol: str, ohlc_data: List[list], coins_file: str):
    coins_dal = CoinsDAL(coins_file)
    prices = []
    for candle in ohlc_data:
        timestamp = int(candle[0]) / 1000  # Convert ms to s
        open_price = candle[1]
        high_price = candle[2]
        low_price = candle[3]
        close_price = candle[4]
        prices.append([timestamp, open_price, high_price, low_price, close_price])
    coins_dal.add_prices_to_coin(symbol, prices)


def add_new_coin_with_history(symbol, coin_id, coins_file, ohlc_data):
    from data_access.DAL.coins_DAL import CoinsDAL

    coins_dal = CoinsDAL(coins_file)
    coins_dal.add_coin(symbol, coin_id)
    fetch_and_add_historic_prices(symbol, ohlc_data, coins_file)


def update_coin_prices(coins_file: str) -> List[Coin]:
    logger.info("Starting coin price update process...")
    coins_dal = CoinsDAL(coins_file)
    local_coins = coins_dal.get_all_coins()
    local_coins_ids = [coin.coin_id for coin in local_coins]

    if len(local_coins) == 0:
        logger.warning("There are no coins in the data store, cannot update prices.")
        return []

    cg = CoinGecko()
    logger.info("Fetching latest market data from CoinGecko...")
    coin_list = cg.get_coins()
    new_coins = 0
    for coin in coin_list:
        if coin.coin_id not in local_coins_ids:
            new_coins += 1
            logger.info(f"New coin '{coin.symbol}' found. Fetching its historical data.")
            ohlc_data = cg.get_historic_ohlc_by_coin_id(coin.coin_id, days=1)
            add_new_coin_with_history(
                coin.symbol,
                coin.coin_id,
                coins_file,
                ohlc_data,
            )
        if len(coin.prices) > 0:
            coins_dal.add_prices_to_coin(coin.symbol, coin.prices)
        coins_dal.update_coin_price_change(coin.symbol, coin.price_change)

    logger.info(f"Price data updated for {len(coin_list)} coins.")
    if new_coins > 0:
        logger.info(
            f"Inserted {new_coins} new coins into the data store due to market cap changes."
        )
    return coin_list
