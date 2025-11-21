"""
Custom exceptions for the application.
"""


class TradingBotException(Exception):
    """Base exception for the application."""


class DataStorageError(TradingBotException):
    """Exception raised for errors in the data storage."""


class MarketDataError(TradingBotException):
    """Exception raised for errors in the market data provider."""


class DecisionEngineError(TradingBotException):
    """Exception raised for errors in the decision engine."""
