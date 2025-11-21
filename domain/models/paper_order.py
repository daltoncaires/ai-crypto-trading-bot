from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Literal


@dataclass
class PaperOrder:
    timestamp: datetime
    buy_price: float
    quantity: float
    symbol: str
    direction: Literal["BUY", "SELL"]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaperOrder":
        timestamp = data.get("timestamp")
        buy_price = data.get("buy_price")
        quantity = data.get("quantity")
        symbol = data.get("symbol")
        direction = data.get("direction")

        if not timestamp or not isinstance(timestamp, str):
            raise ValueError("timestamp is required and must be a string")
        if buy_price is None or not isinstance(buy_price, (float, int)):
            raise ValueError("buy_price is required and must be a float or int")
        if quantity is None or not isinstance(quantity, (float, int)):
            raise ValueError("quantity is required and must be a float or int")
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol is required and must be a string")
        if direction not in ("BUY", "SELL"):
            raise ValueError("direction must be either 'BUY' or 'SELL'")

        return cls(
            timestamp=datetime.fromisoformat(timestamp),
            buy_price=float(buy_price),
            quantity=float(quantity),
            symbol=symbol,
            direction=direction,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "buy_price": self.buy_price,
            "quantity": self.quantity,
            "symbol": self.symbol,
            "direction": self.direction,
        }
