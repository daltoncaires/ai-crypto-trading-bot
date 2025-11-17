from typing import Literal, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaperOrder:
    timestamp: datetime
    buy_price: float
    quantity: float
    symbol: str
    direction: Literal["BUY", "SELL"]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaperOrder":
        return cls(
            timestamp=datetime.fromisoformat(data.get("timestamp")),
            buy_price=data.get("buy_price"),
            quantity=data.get("quantity"),
            symbol=data.get("symbol"),
            direction=data.get("direction"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "buy_price": self.buy_price,
            "quantity": self.quantity,
            "symbol": self.symbol,
            "direction": self.direction,
        }
