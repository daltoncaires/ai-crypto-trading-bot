"""
Binance adapter for market data services.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any

from binance.client import Client
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

    def get_price_by_coin_id(self, coin_id: str) -> Optional[float]:
        logger.debug(f"BinanceAdapter: Fetching price for {coin_id}")
        try:
            ticker = self.client.get_symbol_ticker(symbol=coin_id.upper() + 'USDT')
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"BinanceAdapter: Error fetching price for {coin_id}: {e}")
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
            klines = self.client.get_historical_klines(
                symbol=coin_id.upper() + 'USDT',
                interval=interval,
                limit=days * 24,  # Assuming 1h interval
            )
            return klines
        except Exception as e:
            logger.error(f"BinanceAdapter: Error fetching OHLC for {coin_id}: {e}")
            return []

    def get_coins(self) -> List[Coin]:
        logger.debug("BinanceAdapter: Fetching list of coins")
        try:
            tickers = self.client.get_all_tickers()
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
        except Exception as e:
            logger.error(f"BinanceAdapter: Error fetching coins: {e}")
            return []

    def search_pools(self, query: str | None = None, chain: str | None = None) -> Dict[str, Any]:
        logger.debug(f"BinanceAdapter: Searching pools for query={query}, chain={chain}")
        # Binance API might not have a direct equivalent for "liquidity pools" like CoinGecko.
        # This method might need to be adapted or return empty/NotImplementedError.
        logger.warning("BinanceAdapter: search_pools is not implemented.")
        return {}