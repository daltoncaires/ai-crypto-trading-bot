from abc import ABC, abstractmethod
from typing import List

from domain.models.coin import Coin
from domain.ports.data_storage_port import DataStoragePort
from domain.ports.decision_engine_port import DecisionEnginePort
from utils.load_env import Settings


class StrategyComponent(ABC):
    @abstractmethod
    def __init__(
        self,
        storage: DataStoragePort,
        decision_engine: DecisionEnginePort,
        config: Settings,
    ):
        pass

    @abstractmethod
    def evaluate_and_execute_buy(self, coin: Coin, current_price: float, safe_pools: List[dict]):
        pass

    @abstractmethod
    def evaluate_and_execute_sell(self, coin: Coin, current_price: float):
        pass
