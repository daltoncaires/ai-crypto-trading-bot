"""Adapter for the CoinGecko API."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from domain.models.coin import Coin
from domain.ports.market_data_port import MarketDataPort
from utils.load_env import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class CoinGeckoAdapter(MarketDataPort):
    """An adapter for the CoinGecko API that implements the MarketDataPort."""

    def __init__(self):
        self.root = "https://api.coingecko.com/api/v3"
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": settings.cg_api_key,
        }
        logger.info("CoinGecko adapter initialized.")

    def get_price_by_coin_id(self, coin_id: str) -> Optional[float]:
        request_url = f"{self.root}/simple/price?ids={coin_id}&vs_currencies=usd"
        try:
            response = requests.get(request_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(10)  # Basic rate limiting
            data = response.json()
            return data.get(coin_id, {}).get("usd")
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API request failed for price of {coin_id}: {e}")
            return None

    def get_historic_ohlc_by_coin_id(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 1,
        interval: str = "hourly",
    ) -> List[list]:
        request_url = f"{self.root}/coins/{coin_id}/ohlc?vs_currency={vs_currency}&days={days}&interval={interval}"
        try:
            response = requests.get(request_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(10)  # Basic rate limiting
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API request failed for OHLC of {coin_id}: {e}")
            return []

    def get_coins(self) -> List[Coin]:
        request_url = (
            f"{self.root}/coins/markets?order=market_cap_desc&per_page=10"
            "&vs_currency=usd&price_change_percentage=1h"
        )
        try:
            response = requests.get(request_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(10)  # Basic rate limiting
            data = response.json()
            coins = []
            now = datetime.now().timestamp()
            for coin_data in data:
                coin = Coin(
                    coin_id=coin_data["id"],
                    symbol=coin_data["symbol"],
                    realized_pnl=0.0,
                    price_change=coin_data.get("price_change_percentage_1h_in_currency")
                    or 0.0,
                )
                coin.prices = [[now, coin_data["current_price"]]]
                coins.append(coin)
            return coins
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API request failed for market data: {e}")
            return []

    def search_pools(
        self, query: str | None = None, chain: str | None = None
    ) -> Dict[str, Any]:
        request_url = f"{self.root}/onchain/search/pools?query={query}"
        if chain:
            request_url += f"&chain={chain}"
        try:
            response = requests.get(request_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(10)  # Basic rate limiting
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API request failed for pool search: {e}")
            return {}
