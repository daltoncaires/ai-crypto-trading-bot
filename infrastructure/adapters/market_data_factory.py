"""
Factory for creating market data adapters.
"""
from domain.ports.market_data_port import MarketDataPort
from infrastructure.adapters.binance_adapter import BinanceAdapter
from infrastructure.adapters.coingecko_adapter import CoinGeckoAdapter
from utils.load_env import Settings


def get_market_data_adapter(settings: Settings) -> MarketDataPort:
    """
    Returns a market data adapter based on the settings.
    """
    if settings.market_data_provider == "binance":
        return BinanceAdapter(settings)
    elif settings.market_data_provider == "coingecko":
        return CoinGeckoAdapter(settings)
    else:
        raise ValueError(f"Invalid market data provider: {settings.market_data_provider}")
