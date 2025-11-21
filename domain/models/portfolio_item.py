from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class PnLEntry:
    date: datetime
    value: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PnLEntry":
        entry_date = data.get("date")
        value = data.get("value")

        if not entry_date or not isinstance(entry_date, str):
            raise ValueError("date is required and must be a string")
        if value is None or not isinstance(value, (float, int)):
            raise ValueError("value is required and must be a float or int")

        return cls(
            date=datetime.fromisoformat(entry_date),
            value=float(value),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "value": self.value,
        }


@dataclass
class PortfolioItem:
    cost_basis: float
    total_quantity: float
    symbol: str
    id: Optional[int] = None  # Database primary key
    pnl_entries: List[PnLEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PortfolioItem":
        cost_basis = data.get("cost_basis")
        total_quantity = data.get("total_quantity")
        symbol = data.get("symbol")

        if cost_basis is None or not isinstance(cost_basis, (float, int)):
            raise ValueError("cost_basis is required and must be a float or int")
        if total_quantity is None or not isinstance(total_quantity, (float, int)):
            raise ValueError("total_quantity is required and must be a float or int")
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol is required and must be a string")

        return cls(
            cost_basis=float(cost_basis),
            total_quantity=float(total_quantity),
            symbol=symbol,
            pnl_entries=[PnLEntry.from_dict(p) for p in data.get("pnl_entries", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cost_basis": self.cost_basis,
            "total_quantity": self.total_quantity,
            "symbol": self.symbol,
            "pnl_entries": [p.to_dict() for p in self.pnl_entries],
        }
