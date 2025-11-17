from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Coin:
    coin_id: str
    symbol: str
    realized_pnl: float = 0.0
    price_change: float = 0.0
    prices: List[list] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Coin':
        return cls(
            coin_id=data.get('coinId'),
            symbol=data.get('symbol'),
            realized_pnl=data.get('realizedPnl', 0.0),
            price_change=data.get('priceChange') or 0.0,
            prices=data.get('prices', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'coinId': self.coin_id,
            'symbol': self.symbol,
            'realizedPnl': self.realized_pnl,
            'priceChange': self.price_change,
            'prices': self.prices
        }
