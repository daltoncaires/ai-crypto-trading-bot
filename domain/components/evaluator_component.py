from abc import ABC, abstractmethod
from typing import List

from domain.models.coin import Coin
from domain.ports.market_data_port import MarketDataPort
from utils.load_env import Settings


class EvaluatorComponent(ABC):
    @abstractmethod
    def __init__(self, market_data: MarketDataPort, config: Settings):
        pass

    @abstractmethod
    def is_candidate(self, coin: Coin) -> bool:
        pass

    @abstractmethod
    def check_liquidity_pools(self, coin: Coin) -> List[dict]:
        pass
