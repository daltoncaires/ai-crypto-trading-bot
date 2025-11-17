"""
Defines the interface (port) for data storage services.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Literal
from datetime import datetime

from domain.models.coin import Coin
from domain.models.paper_order import PaperOrder
from domain.models.portfolio_item import PortfolioItem, PnLEntry


class DataStoragePort(ABC):
    """
    An abstract base class for storing and retrieving trading data,
    combining coin, order, and portfolio operations.
    """

    # --- Coin Methods ---
    @abstractmethod
    def get_all_coins(self) -> List[Coin]:
        raise NotImplementedError

    @abstractmethod
    def get_coin_by_symbol(self, symbol: str) -> Optional[Coin]:
        raise NotImplementedError

    @abstractmethod
    def add_coin(
        self,
        symbol: str,
        coin_id: str,
        realized_pnl: float = 0.0,
        price_change: float = 0.0,
    ) -> Optional[Coin]:
        raise NotImplementedError

    @abstractmethod
    def add_prices_to_coin(
        self, symbol: str, prices: List[list]
    ) -> Optional[List[list]]:
        raise NotImplementedError

    @abstractmethod
    def update_coin_price_change(
        self, symbol: str, price_change: float
    ) -> Optional[Coin]:
        raise NotImplementedError

    @abstractmethod
    def update_coin_pnl(self, symbol: str, new_realized_pnl: float) -> Optional[Coin]:
        raise NotImplementedError

    # --- Order Methods ---
    @abstractmethod
    def get_all_orders(
        self, direction: Optional[Literal["BUY", "SELL"]] = None
    ) -> List[PaperOrder]:
        raise NotImplementedError

    @abstractmethod
    def insert_order(
        self,
        timestamp: datetime,
        buy_price: float,
        quantity: float,
        symbol: str,
        direction: str,
    ) -> PaperOrder:
        raise NotImplementedError

    # --- Portfolio Methods ---
    @abstractmethod
    def get_all_portfolio_items(self) -> List[PortfolioItem]:
        raise NotImplementedError

    @abstractmethod
    def get_portfolio_item_by_symbol(self, symbol: str) -> Optional[PortfolioItem]:
        raise NotImplementedError

    @abstractmethod
    def insert_portfolio_item(
        self, symbol: str, cost_basis: float, total_quantity: float
    ) -> PortfolioItem:
        raise NotImplementedError

    @abstractmethod
    def update_portfolio_item_by_symbol(
        self, symbol: str, cost_basis: float, additional_quantity: float
    ) -> Optional[PortfolioItem]:
        raise NotImplementedError

    @abstractmethod
    def add_pnl_entry_by_symbol(
        self, symbol: str, date: datetime, value: float
    ) -> Optional[PnLEntry]:
        raise NotImplementedError
