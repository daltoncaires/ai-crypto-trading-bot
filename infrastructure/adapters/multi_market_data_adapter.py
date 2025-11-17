"""
Multi-exchange market data adapter.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any

from domain.ports.market_data_port import MarketDataPort
from domain.models.coin import Coin
from utils.logger import get_logger
from utils.load_env import Settings

logger = get_logger(__name__)


class MultiMarketDataAdapter(MarketDataPort):
    """
    An adapter that aggregates market data from multiple sources.
    It tries to fetch data from adapters in the order they are provided.
    """

    def __init__(self, adapters: List[MarketDataPort], config: Settings):
        self.adapters = adapters
        self.config = config
        logger.info(f"MultiMarketDataAdapter initialized with {len(adapters)} adapters.")

    def get_price_by_coin_id(self, coin_id: str) -> Optional[float]:
        for adapter in self.adapters:
            try:
                price = adapter.get_price_by_coin_id(coin_id)
                if price is not None:
                    logger.debug(f"Price for {coin_id} fetched from {adapter.__class__.__name__}")
                    return price
            except Exception as e:
                logger.warning(f"Failed to get price from {adapter.__class__.__name__}: {e}")
        logger.warning(f"Could not fetch price for {coin_id} from any adapter.")
        return None

    def get_historic_ohlc_by_coin_id(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 1,
        interval: str = "hourly",
    ) -> List[list]:
        for adapter in self.adapters:
            try:
                ohlc_data = adapter.get_historic_ohlc_by_coin_id(coin_id, vs_currency, days, interval)
                if ohlc_data:
                    logger.debug(f"OHLC data for {coin_id} fetched from {adapter.__class__.__name__}")
                    return ohlc_data
            except Exception as e:
                logger.warning(f"Failed to get OHLC data from {adapter.__class__.__name__}: {e}")
        logger.warning(f"Could not fetch OHLC data for {coin_id} from any adapter.")
        return []

    def get_coins(self) -> List[Coin]:
        all_coins = []
        for adapter in self.adapters:
            try:
                coins = adapter.get_coins()
                if coins:
                    logger.debug(f"Coins fetched from {adapter.__class__.__name__}")
                    all_coins.extend(coins)
                    # For get_coins, we might want to aggregate or return the first successful list
                    # For now, we'll extend and return unique coins later if needed.
                    # Or, if we want only one source, we can return here.
                    return coins # Return first successful list for simplicity
            except Exception as e:
                logger.warning(f"Failed to get coins from {adapter.__class__.__name__}: {e}")
        logger.warning("Could not fetch coins from any adapter.")
        return all_coins

    def search_pools(self, query: str | None = None, chain: str | None = None) -> Dict[str, Any]:
        for adapter in self.adapters:
            try:
                pools = adapter.search_pools(query, chain)
                if pools:
                    logger.debug(f"Pools for query={query} fetched from {adapter.__class__.__name__}")
                    return pools
            except Exception as e:
                logger.warning(f"Failed to search pools from {adapter.__class__.__name__}: {e}")
        logger.warning(f"Could not search pools for query={query} from any adapter.")
        return {}
