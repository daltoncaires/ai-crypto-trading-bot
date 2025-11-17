from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class PnLEntry:
    date: datetime
    value: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PnLEntry":
        return cls(
            date=datetime.fromisoformat(data.get("date")),
            value=data.get("value"),
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
    pnl_entries: List[PnLEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PortfolioItem":
        return cls(
            cost_basis=data.get("cost_basis"),
            total_quantity=data.get("total_quantity"),
            symbol=data.get("symbol"),
            pnl_entries=[PnLEntry.from_dict(p) for p in data.get("pnl_entries", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cost_basis": self.cost_basis,
            "total_quantity": self.total_quantity,
            "symbol": self.symbol,
            "pnl_entries": [p.to_dict() for p in self.pnl_entries],
        }
