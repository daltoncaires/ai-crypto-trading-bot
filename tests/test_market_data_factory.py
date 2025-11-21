from unittest.mock import Mock

import pytest

from infrastructure.adapters.binance_adapter import BinanceAdapter
from infrastructure.adapters.coingecko_adapter import CoinGeckoAdapter
from infrastructure.adapters.market_data_factory import get_market_data_adapter
from utils.load_env import Settings


def test_get_market_data_adapter_binance():
    """
    Tests that the factory returns a BinanceAdapter when the provider is set to 'binance'.
    """
    settings = Mock(spec=Settings)
    settings.market_data_provider = "binance"
    adapter = get_market_data_adapter(settings)
    assert isinstance(adapter, BinanceAdapter)

def test_get_market_data_adapter_coingecko():
    """
    Tests that the factory returns a CoinGeckoAdapter when the provider is set to 'coingecko'.
    """
    settings = Mock(spec=Settings)
    settings.market_data_provider = "coingecko"
    adapter = get_market_data_adapter(settings)
    assert isinstance(adapter, CoinGeckoAdapter)

def test_get_market_data_adapter_invalid():
    """
    Tests that the factory raises a ValueError when an invalid provider is set.
    """
    settings = Mock(spec=Settings)
    settings.market_data_provider = "invalid_provider"
    with pytest.raises(ValueError):
        get_market_data_adapter(settings)
