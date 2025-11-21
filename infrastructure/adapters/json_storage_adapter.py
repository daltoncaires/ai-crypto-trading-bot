"""
Adapter for storing and retrieving trading data from JSON files.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Callable, cast, List, Literal, Optional

from domain.models.coin import Coin
from domain.models.paper_order import PaperOrder
from domain.models.portfolio_item import PnLEntry, PortfolioItem
from domain.ports.data_storage_port import DataStoragePort
from utils.logger import get_logger

logger = get_logger(__name__)


class JSONStorageAdapter(DataStoragePort):
    """
    An adapter that implements the DataStoragePort for a JSON file-based
    storage system.
    """

    def __init__(self, coins_file: str, orders_file: str, portfolio_file: str):
        self.coins_file = coins_file
        self.orders_file = orders_file
        self.portfolio_file = portfolio_file
        logger.info(
            "JSON Storage Adapter initialized with files: "
            f"{coins_file}, {orders_file}, {portfolio_file}"
        )

    # --- Private Helper Methods ---

    def _read_data(self, file_path: str) -> List[Any]:
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r") as f:
                data = f.read().strip()
                if not data:
                    return []
                return cast(List[Any], json.loads(data))
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading from {file_path}: {e}")
            return []

    def _write_data(self, file_path: str, items: List[Any]):
        try:
            with open(file_path, "w") as f:
                f.write(json.dumps(items, default=str))
        except IOError as e:
            logger.error(f"Error writing to {file_path}: {e}")

    # --- Coin Methods ---

    def get_all_coins(self) -> List[Coin]:
        data = self._read_data(self.coins_file)
        return [Coin.from_dict(c) for c in data]

    def get_coin_by_symbol(self, symbol: str) -> Optional[Coin]:
        return next((c for c in self.get_all_coins() if c.symbol == symbol), None)

    def add_coin(
        self,
        symbol: str,
        coin_id: str,
        realized_pnl: float = 0.0,
        price_change: float = 0.0,
    ) -> Optional[Coin]:
        coins = self.get_all_coins()
        if any(c.symbol == symbol for c in coins):
            logger.warning(f"Coin '{symbol}' already exists. Cannot add duplicate.")
            return None
        new_coin = Coin(
            symbol=symbol,
            coin_id=coin_id,
            realized_pnl=realized_pnl,
            prices=[],
            price_change=price_change,
        )
        coins.append(new_coin)
        self._write_data(self.coins_file, [c.to_dict() for c in coins])
        return new_coin

    def add_prices_to_coin(
        self, symbol: str, prices: List[list]
    ) -> Optional[List[list]]:
        coins = self.get_all_coins()
        for coin in coins:
            if coin.symbol == symbol:
                coin.prices.extend(prices)
                self._write_data(self.coins_file, [c.to_dict() for c in coins])
                return prices
        return None

    def update_coin_price_change(
        self, symbol: str, price_change: float
    ) -> Optional[Coin]:
        coins = self.get_all_coins()
        for coin in coins:
            if coin.symbol == symbol:
                coin.price_change = price_change
                self._write_data(self.coins_file, [c.to_dict() for c in coins])
                return coin
        return None

    def update_coin_pnl(self, symbol: str, new_realized_pnl: float) -> Optional[Coin]:
        coins = self.get_all_coins()
        for coin in coins:
            if coin.symbol == symbol:
                coin.realized_pnl = new_realized_pnl
                break
        else:
            return None
        self._write_data(self.coins_file, [c.to_dict() for c in coins])
        return coin

    # --- Order Methods ---

    def get_all_orders(
        self, direction: Optional[Literal["BUY", "SELL"]] = None
    ) -> List[PaperOrder]:
        data = self._read_data(self.orders_file)
        orders = [PaperOrder.from_dict(o) for o in data]
        if direction:
            orders = [o for o in orders if o.direction == direction]
        return orders

    def insert_order(
        self,
        timestamp: datetime,
        buy_price: float,
        quantity: float,
        symbol: str,
        direction: Literal["BUY", "SELL"],
    ) -> PaperOrder:
        orders = self.get_all_orders()
        new_order = PaperOrder(
            timestamp=timestamp,
            buy_price=buy_price,
            quantity=quantity,
            symbol=symbol,
            direction=direction,
        )
        orders.append(new_order)
        self._write_data(self.orders_file, [o.to_dict() for o in orders])
        return new_order

    # --- Portfolio Methods ---

    def get_all_portfolio_items(self) -> List[PortfolioItem]:
        data = self._read_data(self.portfolio_file)
        return [PortfolioItem.from_dict(p) for p in data]

    def get_portfolio_item_by_symbol(self, symbol: str) -> Optional[PortfolioItem]:
        return next(
            (item for item in self.get_all_portfolio_items() if item.symbol == symbol),
            None,
        )

    def insert_portfolio_item(
        self, symbol: str, cost_basis: float, total_quantity: float
    ) -> PortfolioItem:
        items = self.get_all_portfolio_items()
        new_item = PortfolioItem(
            symbol=symbol, cost_basis=cost_basis, total_quantity=total_quantity
        )
        items.append(new_item)
        self._write_data(self.portfolio_file, [i.to_dict() for i in items])
        return new_item

    def update_portfolio_item_by_symbol(
        self, symbol: str, cost_basis: float, additional_quantity: float
    ) -> Optional[PortfolioItem]:
        items = self.get_all_portfolio_items()
        for item in items:
            if item.symbol == symbol:
                item.cost_basis = cost_basis
                item.total_quantity += additional_quantity
                self._write_data(self.portfolio_file, [i.to_dict() for i in items])
                return item
        return None

    def add_pnl_entry_by_symbol(
        self, symbol: str, date: datetime, value: float
    ) -> Optional[PnLEntry]:
        items = self.get_all_portfolio_items()
        for item in items:
            if item.symbol == symbol:
                pnl_entry = PnLEntry(date=date, value=value)
                item.pnl_entries.append(pnl_entry)
                self._write_data(self.portfolio_file, [i.to_dict() for i in items])
                return pnl_entry
        return None
