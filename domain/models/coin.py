from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Coin:
    coin_id: str
    symbol: str
    id: Optional[int] = None  # Database primary key
    realized_pnl: float = 0.0
    price_change: float = 0.0
    prices: List[list] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Coin":
        coin_id = data.get("coinId")
        symbol = data.get("symbol")
        if not coin_id or not isinstance(coin_id, str):
            raise ValueError("coin_id is required and must be a string")
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol is required and must be a string")

        return cls(
            coin_id=coin_id,
            symbol=symbol,
            realized_pnl=data.get("realizedPnl", 0.0),
            price_change=data.get("priceChange") or 0.0,
            prices=data.get("prices", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'coinId': self.coin_id,
            'symbol': self.symbol,
            'realizedPnl': self.realized_pnl,
            'priceChange': self.price_change,
            'prices': self.prices
        }
