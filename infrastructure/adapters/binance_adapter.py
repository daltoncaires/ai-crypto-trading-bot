"""
Binance adapter for market data services.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from domain.models.coin import Coin
from domain.ports.market_data_port import MarketDataPort
from utils.load_env import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BinanceAdapter(MarketDataPort):
    """
    A concrete implementation of MarketDataPort for Binance.
    """

    def __init__(self, config: Settings):
        self.config = config
        self.client = Client(config.binance_api_key, config.binance_api_secret)
        logger.info("BinanceAdapter initialized.")

    def _get_retrying_api_call(self, api_call_func):
        @retry(
            stop=stop_after_attempt(self.config.api.max_retries),
            wait=wait_exponential(
                multiplier=self.config.api.retry_multiplier,
                min=self.config.api.retry_min_delay,
                max=self.config.api.rate_limit_sleep,
            ),
            retry=retry_if_exception_type((BinanceAPIException, requests.exceptions.RequestException)),
            reraise=True,
        )
        def _retrying_api_call(*args, **kwargs):
            return api_call_func(*args, **kwargs)
        return _retrying_api_call

    def get_price_by_coin_id(self, coin_id: str) -> Optional[float]:
        logger.debug(f"BinanceAdapter: Fetching price for {coin_id}")
        try:
            ticker = self._get_retrying_api_call(self.client.get_symbol_ticker)(symbol=coin_id.upper() + 'USDT')
            return float(ticker['price'])
        except (BinanceAPIException, requests.exceptions.RequestException) as e:
            logger.error(f"BinanceAdapter: Error fetching price for {coin_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"BinanceAdapter: Unexpected error fetching price for {coin_id}: {e}")
            return None

    def get_historic_ohlc_by_coin_id(
        self,
        coin_id: str,
        vs_currency: str = "usdt",
        days: int = 1,
        interval: str = "1h",
    ) -> List[list]:
        logger.debug(f"BinanceAdapter: Fetching historical OHLC for {coin_id}")
        try:
            # Binance interval mapping could be needed
            # For simplicity, using direct values
            klines = self._get_retrying_api_call(self.client.get_historical_klines)(
                symbol=coin_id.upper() + 'USDT',
                interval=interval,
                limit=days * 24,  # Assuming 1h interval
            )
            return klines  # type: ignore[no-any-return]
        except (BinanceAPIException, requests.exceptions.RequestException) as e:
            logger.error(f"BinanceAdapter: Error fetching OHLC for {coin_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"BinanceAdapter: Unexpected error fetching OHLC for {coin_id}: {e}")
            return []

    def get_historical_data(
        self, symbol: str, interval: str, limit: int
    ) -> pd.DataFrame:
        logger.debug(
            f"BinanceAdapter: Fetching {limit} klines for {symbol} with interval {interval}"
        )
        try:
            klines = self._get_retrying_api_call(self.client.get_historical_klines)(
                symbol=symbol, interval=interval, limit=limit
            )
            df = pd.DataFrame(
                klines,
                columns=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "quote_asset_volume",
                    "number_of_trades",
                    "taker_buy_base_asset_volume",
                    "taker_buy_quote_asset_volume",
                    "ignore",
                ],
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            # Convert columns to numeric, as Binance returns strings
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col])
            return df[
                ["timestamp", "open", "high", "low", "close", "volume"]
            ]
        except (BinanceAPIException, requests.exceptions.RequestException) as e:
            logger.error(
                f"BinanceAdapter: Error fetching historical klines for {symbol}: {e}"
            )
            return pd.DataFrame()
        except Exception as e:
            logger.error(
                f"BinanceAdapter: Unexpected error fetching historical klines for {symbol}: {e}"
            )
            return pd.DataFrame()

    def get_coins(self) -> List[Coin]:
        logger.debug("BinanceAdapter: Fetching list of coins")
        try:
            tickers = self._get_retrying_api_call(self.client.get_all_tickers)()
            coins = []
            for ticker in tickers:
                if ticker['symbol'].endswith('USDT'):
                    coin = Coin(
                        coin_id=ticker['symbol'].replace('USDT', '').lower(),
                        symbol=ticker['symbol'].replace('USDT', ''),
                        realized_pnl=0.0,
                        price_change=0.0,  # Binance API for 24hr change is separate
                    )
                    coin.prices = [[0, float(ticker['price'])]]
                    coins.append(coin)
            return coins
        except (BinanceAPIException, requests.exceptions.RequestException) as e:
            logger.error(f"BinanceAdapter: Error fetching coins: {e}")
            return []
        except Exception as e:
            logger.error(f"BinanceAdapter: Unexpected error fetching coins: {e}")
            return []

    def search_pools(self, query: str | None = None, chain: str | None = None) -> Dict[str, Any]:
        logger.debug(f"BinanceAdapter: Searching pools for query={query}, chain={chain}")
        # Binance API might not have a direct equivalent for "liquidity pools" like CoinGecko.
        # This method might need to be adapted or return empty/NotImplementedError.
        try:
            # Example of how you might use the retrying call if there was an actual API call
            # For now, it just logs a warning and returns an empty dict.
            # result = self._get_retrying_api_call(some_binance_pool_api_call)(query=query, chain=chain)
            logger.warning("BinanceAdapter: search_pools is not fully implemented and returns an empty dict.")
            return {}
        except (BinanceAPIException, requests.exceptions.RequestException) as e:
            logger.error(f"BinanceAdapter: Error searching pools: {e}")
            return {}
        except Exception as e:
            logger.error(f"BinanceAdapter: Unexpected error searching pools: {e}")
            return {}
