from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from utils.load_env import Settings
from domain.evaluator import Evaluator
from domain.ports.data_storage_port import DataStoragePort
from domain.ports.market_data_port import MarketDataPort
from domain.strategy import Strategy


class EngineComponent(ABC):
    @abstractmethod
    def __init__(
        self,
        storage: DataStoragePort,
        market_data: MarketDataPort,
        evaluator: Evaluator,
        strategy: Strategy,
        config: Settings,
        loop_interval: int = 3600,
    ):
        pass

    @abstractmethod
    def run(self, run_once: bool = False) -> None:
        pass
