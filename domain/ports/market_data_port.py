"""
Defines the interface (port) for market data services.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from domain.models.coin import Coin


class MarketDataPort(ABC):
    """An abstract base class for market data providers."""

    @abstractmethod
    def get_price_by_coin_id(self, coin_id: str) -> Optional[float]:
        """Fetches the current price for a given coin ID."""
        raise NotImplementedError

    @abstractmethod
    def get_historic_ohlc_by_coin_id(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 1,
        interval: str = "hourly",
    ) -> List[list]:
        """Fetches historical OHLC data for a coin."""
        raise NotImplementedError

    @abstractmethod
    def get_coins(self) -> List[Coin]:
        """Fetches a list of top coins with market data."""
        raise NotImplementedError

    @abstractmethod
    def search_pools(self, query: str | None = None, chain: str | None = None) -> Dict[str, Any]:
        """Searches for liquidity pools."""
        raise NotImplementedError
