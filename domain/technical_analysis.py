"""
A module for calculating technical analysis indicators.
It prioritizes the use of the 'ta-lib' library for performance, with a
fallback to 'pandas_ta' if 'ta-lib' is not available.
"""
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import talib
    TA_LIB_AVAILABLE = True
    logger.info("TA-Lib found. Using TA-Lib for technical analysis.")
except ImportError:
    import pandas_ta as ta
    TA_LIB_AVAILABLE = False
    logger.warning(
        "TA-Lib not found. Falling back to pandas_ta. "
        "For better performance, consider installing TA-Lib."
    )

def calculate_rsi(close_prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI).

    Args:
        close_prices: A pandas Series of closing prices.
        period: The time period for the RSI calculation.

    Returns:
        A pandas Series containing the RSI values.
    """
    if TA_LIB_AVAILABLE:
        return talib.RSI(close_prices, timeperiod=period)
    else:
        return ta.rsi(close_prices, length=period)

# Add other indicators here following the same pattern, e.g.:
# def calculate_ema(close_prices: pd.Series, period: int = 20) -> pd.Series:
#     if TA_LIB_AVAILABLE:
#         return talib.EMA(close_prices, timeperiod=period)
#     else:
#         return ta.ema(close_prices, length=period)

