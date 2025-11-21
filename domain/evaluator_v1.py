"""
Encapsulates the logic for evaluating trading candidates.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List

from domain.components.evaluator_component import EvaluatorComponent
from domain.models.coin import Coin
from utils.load_env import Settings
from utils.logger import get_logger

if TYPE_CHECKING:
    from domain.ports.market_data_port import MarketDataPort

logger = get_logger(__name__)


class EvaluatorV1(EvaluatorComponent):
    """
    Evaluates coins to determine if they are viable candidates for trading.
    This is version 1.
    """

    def __init__(self, market_data: MarketDataPort, config: Settings):
        self.market_data = market_data
        self.config = config
        logger.info("EvaluatorV1 component initialized.")

    def is_candidate(self, coin: Coin) -> bool:
        """
        Checks if a coin meets the basic criteria for a trade analysis.
        """
        if coin.price_change < self.config.trade.price_change_threshold:
            logger.debug(
                f"Skipping {coin.symbol} due to low price change: "
                f"{coin.price_change} < {self.config.trade.price_change_threshold}"
            )
            return False
        return True

    def check_liquidity_pools(self, coin: Coin) -> List[dict]:
        """
        Checks for sufficiently liquid pools for a given coin.
        """
        logger.debug(f"Checking liquidity pools for {coin.symbol}...")
        pools_response = self.market_data.search_pools(coin.symbol)
        pools_data = (
            pools_response.get("data", []) if isinstance(pools_response, dict) else []
        )
        safe_pools = []
        for pool in pools_data:
            reserve = pool.get("reserve_in_usd", 0)
            volume = pool.get("volume_in_usd", {}).get("h24", 0)
            buys = pool.get("buys_24h", 0)
            if (
                reserve >= self.config.pool.min_reserves_usd
                and volume >= self.config.pool.min_volume_24h
                and buys >= self.config.pool.min_buys_24h
            ):
                safe_pools.append(pool)
        logger.debug(f"Found {len(safe_pools)} safe pools for {coin.symbol}.")
        return safe_pools
