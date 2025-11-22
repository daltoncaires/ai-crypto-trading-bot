"""
Factory for creating market data adapters.
"""
from domain.ports.market_data_port import MarketDataPort
from infrastructure.adapters.binance_adapter import BinanceAdapter
from infrastructure.adapters.coingecko_adapter import CoinGeckoAdapter
from infrastructure.adapters.multi_market_data_adapter import MultiMarketDataAdapter
from utils.load_env import Settings


def get_market_data_adapter(settings: Settings) -> MarketDataPort:
    """
    Returns a market data adapter based on the settings.
    It always returns a MultiMarketDataAdapter that prioritizes the configured
    provider and uses the other as a fallback.
    """
    if settings.market_data_provider == "binance":
        binance_adapter = BinanceAdapter(settings)
        coingecko_adapter = CoinGeckoAdapter(settings)
        return MultiMarketDataAdapter(adapters=[binance_adapter, coingecko_adapter], config=settings)
    elif settings.market_data_provider == "coingecko":
        coingecko_adapter = CoinGeckoAdapter(settings)
        binance_adapter = BinanceAdapter(settings)
        return MultiMarketDataAdapter(adapters=[coingecko_adapter, binance_adapter], config=settings)
    else:
        # This case should ideally not be reached if load_settings handles it correctly
        raise ValueError(f"Invalid market data provider configured: {settings.market_data_provider}")
