"""Adapter for the CoinGecko API."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from domain.models.coin import Coin
from domain.ports.market_data_port import MarketDataPort
from utils.load_env import Settings  # Import Settings
from utils.logger import get_logger  # Moved to top

logger = get_logger(__name__)


class CoinGeckoAdapter(MarketDataPort):
    """An adapter for the CoinGecko API that implements the MarketDataPort."""

    def __init__(self, config: Settings) -> None:
        self.config = config
        self.root = self.config.coingecko.api_root
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": self.config.cg_api_key,
        }
        logger.info("CoinGecko adapter initialized.")

    def _get_retrying_api_call(self, api_call_func):
        @retry(
            stop=stop_after_attempt(self.config.api.max_retries),
            wait=wait_exponential(
                multiplier=self.config.api.retry_multiplier,
                min=self.config.api.retry_min_delay,
                max=self.config.api.rate_limit_sleep,
            ),
            retry=retry_if_exception_type(requests.exceptions.RequestException),
            reraise=True,
        )
        def _retrying_api_call(*args, **kwargs):
            return api_call_func(*args, **kwargs)
        return _retrying_api_call

    def get_price_by_coin_id(self, coin_id: str) -> Optional[float]:
        request_url = f"{self.root}/simple/price?ids={coin_id}&vs_currencies=usd"
        start_time = time.monotonic()
        try:
            response = self._get_retrying_api_call(requests.get)(request_url, headers=self.headers, timeout=self.config.api.request_timeout)
            response.raise_for_status()
            duration = time.monotonic() - start_time
            logger.info(
                "CoinGecko API call successful",
                extra={"event": "api_call", "adapter": "coingecko", "endpoint": "/simple/price", "duration_ms": duration * 1000},
            )
            data = response.json()
            return data.get(coin_id, {}).get("usd")  # type: ignore[no-any-return]
        except requests.exceptions.RequestException as e:
            duration = time.monotonic() - start_time
            logger.error(
                f"CoinGecko API request failed for price of {coin_id}: {e}",
                extra={"event": "api_error", "adapter": "coingecko", "endpoint": "/simple/price", "duration_ms": duration * 1000},
            )
            return None

    def get_historic_ohlc_by_coin_id(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 1,
        interval: str = "hourly",
    ) -> List[list]:
        # NOTE: CoinGecko's 'interval' parameter is not supported on the /ohlc endpoint.
        # The granularity is determined by the 'days' parameter.
        request_url = f"{self.root}/coins/{coin_id}/ohlc?vs_currency={vs_currency}&days={days}"
        start_time = time.monotonic()
        try:
            response = self._get_retrying_api_call(requests.get)(request_url, headers=self.headers, timeout=self.config.api.request_timeout)
            response.raise_for_status()
            duration = time.monotonic() - start_time
            logger.info(
                "CoinGecko API call successful",
                extra={"event": "api_call", "adapter": "coingecko", "endpoint": "/coins/{id}/ohlc", "duration_ms": duration * 1000},
            )
            return response.json()  # type: ignore[no-any-return]
        except requests.exceptions.RequestException as e:
            duration = time.monotonic() - start_time
            logger.error(
                f"CoinGecko API request failed for OHLC of {coin_id}: {e}",
                extra={"event": "api_error", "adapter": "coingecko", "endpoint": "/coins/{id}/ohlc", "duration_ms": duration * 1000},
            )
            return []

    def get_historical_data(
        self, symbol: str, interval: str, limit: int
    ) -> pd.DataFrame:
        # NOTE: This is a simplification. CoinGecko uses 'coin_id' (e.g., 'bitcoin')
        # not a trading symbol (e.g., 'BTCUSDT'). We assume 'symbol' is the coin_id.
        # The 'interval' and 'limit' parameters are not directly supported.
        # We use 'days' to control the amount of data.
        # For this implementation, we'll map 'limit' to 'days' assuming daily data.
        logger.debug(
            f"CoinGeckoAdapter: Fetching historical data for {symbol}."
        )
        ohlc_data = self.get_historic_ohlc_by_coin_id(coin_id=symbol, days=limit)
        if not ohlc_data:
            return pd.DataFrame()

        df = pd.DataFrame(ohlc_data, columns=["timestamp", "open", "high", "low", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        # CoinGecko does not provide volume in this endpoint, so we add a column of zeros.
        df["volume"] = 0.0
        return df

    def get_coins(self) -> List[Coin]:
        request_url = (
            f"{self.root}/coins/markets?order=market_cap_desc&per_page={self.config.coingecko.coins_per_page}"
            "&vs_currency=usd&price_change_percentage=1h"
        )
        start_time = time.monotonic()
        try:
            response = self._get_retrying_api_call(requests.get)(request_url, headers=self.headers, timeout=self.config.api.request_timeout)
            response.raise_for_status()
            duration = time.monotonic() - start_time
            logger.info(
                "CoinGecko API call successful",
                extra={"event": "api_call", "adapter": "coingecko", "endpoint": "/coins/markets", "duration_ms": duration * 1000},
            )
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
            duration = time.monotonic() - start_time
            logger.error(
                f"CoinGecko API request failed for market data: {e}",
                extra={"event": "api_error", "adapter": "coingecko", "endpoint": "/coins/markets", "duration_ms": duration * 1000},
            )
            return []

    def search_pools(
        self, query: str | None = None, chain: str | None = None
    ) -> Dict[str, Any]:
        request_url = f"{self.root}/onchain/search/pools?query={query}"
        if chain:
            request_url += f"&chain={chain}"
        start_time = time.monotonic()
        try:
            response = self._get_retrying_api_call(requests.get)(request_url, headers=self.headers, timeout=self.config.api.request_timeout)
            response.raise_for_status()
            duration = time.monotonic() - start_time
            logger.info(
                "CoinGecko API call successful",
                extra={"event": "api_call", "adapter": "coingecko", "endpoint": "/onchain/search/pools", "duration_ms": duration * 1000},
            )
            return response.json()  # type: ignore[no-any-return]
        except requests.exceptions.RequestException as e:
            duration = time.monotonic() - start_time
            logger.error(
                f"CoinGecko API request failed for pool search: {e}",
                extra={"event": "api_error", "adapter": "coingecko", "endpoint": "/onchain/search/pools", "duration_ms": duration * 1000},
            )
            return {}
