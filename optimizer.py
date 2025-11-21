"""
Walk-Forward Optimizer for the AI Crypto Trading Bot.

This module implements a Walk-Forward Optimization (WFO) framework to find and
validate trading strategy parameters over time, preventing overfitting and
providing a more realistic performance assessment.

Core Concepts Implemented:
- Vectorized Backtesting with `vectorbt`: For high-speed performance
  calculations, including realistic costs.
- Walk-Forward Optimization (WFO): To simulate real-world performance by
  training on past data and validating on unseen future data.
- Hyperparameter Optimization with `Optuna`: To find the best
  strategy parameters in each training window.
- Flywheel Effect: The best parameters found are saved and can be used as
  new defaults for the live trading bot.
"""

import functools
import json
import os
import sys

import numpy as np
import optuna
import pandas as pd
import vectorbt as vbt

from infrastructure.adapters.json_storage_adapter import JSONStorageAdapter
from utils.logger import get_logger

logger = get_logger(__name__)

# --- Configuration ---
N_FOLDS = 5  # Number of folds for Walk-Forward Optimization
TRAIN_TEST_SPLIT = 0.8  # 80% training, 20% testing in each fold
N_TRIALS = 100  # Number of optimization trials per fold
PARAMS_FILE = "best_params.json"
# The optimizer uses the same data files as the main bot
COINS_FILE = os.path.join(os.path.dirname(__file__), "data/coins.json")
ORDERS_FILE = os.path.join(os.path.dirname(__file__), "data/orders.json")
PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), "data/portfolio.json")

TARGET_SYMBOL = "btc"  # Symbol to optimize for
TRANSACTION_FEES = 0.001  # Binance VIP level 0 taker fee is 0.1%
# ... (rest of the file is the same)
def load_price_data(symbol: str) -> pd.Series:
    """
    Loads historical price data for a single coin from the JSON data store
    and returns it as a pandas Series.
    """
    logger.info(f"Loading historical data for {symbol}...")
    storage = JSONStorageAdapter(
        coins_file=COINS_FILE,
        orders_file=ORDERS_FILE,
        portfolio_file=PORTFOLIO_FILE,
    )
    coin = storage.get_coin_by_symbol(symbol)
    if not coin or not coin.prices:
        raise ValueError(f"No historical data found for symbol: {symbol}")

    # Convert to DataFrame and set a proper DatetimeIndex
    df = pd.DataFrame(coin.prices, columns=["timestamp", "open", "high", "low", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.set_index("timestamp")
    df = df.sort_index()

    # vectorbt works with Series, so we'll use the closing price
    price_series = df["close"]
    logger.info(f"Loaded {len(price_series)} data points for {symbol}.")
    return price_series


def run_backtest(price_series: pd.Series, params: dict) -> vbt.Portfolio:
    """
    Runs a vectorized backtest for a given price series and strategy parameters.

    NOTE: This is a placeholder for the real strategy. The AI-driven,
    per-datapoint decision logic is not easily vectorizable. This example uses
    a simple Moving Average Crossover strategy to demonstrate the `vectorbt`
    and WFO structure.
    """
    fast_ma = vbt.MA.run(price_series, params["fast_window"], short_name="fast")
    slow_ma = vbt.MA.run(price_series, params["slow_window"], short_name="slow")

    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    portfolio = vbt.Portfolio.from_signals(
        price_series,
        entries,
        exits,
        fees=TRANSACTION_FEES,
        sl_stop=params["stop_loss"],
        tp_stop=params["take_profit"],
        freq="D",  # Assuming daily frequency for now
    )
    return portfolio


def run_wfo(price_series: pd.Series):
    """
    Orchestrates the Walk-Forward Optimization process.
    """
    logger.info("--- Starting Walk-Forward Optimization ---")

    # Use vectorbt's built-in splitter for robust windowing
    splitter = vbt.Splitter.from_rolling(
        price_series,
        N_FOLDS,
        min_len=int(len(price_series) / N_FOLDS),
        train_test_split=TRAIN_TEST_SPLIT,
    )

    fold_results = []
    latest_best_params = {}

    for i, (train_idx, test_idx) in enumerate(splitter.split()):
        logger.info(f"--- Processing Fold {i+1}/{N_FOLDS} ---")

        train_prices = price_series.iloc[train_idx]
        test_prices = price_series.iloc[test_idx]

        logger.info(
            f"Train period: {train_prices.index[0]} to {train_prices.index[-1]} "
            f"({len(train_prices)} points)"
        )
        logger.info(
            f"Test period:  {test_prices.index[0]} to {test_prices.index[-1]} "
            f"({len(test_prices)} points)"
        )

        # --- Optimization Step with Optuna ---
        def objective(trial: optuna.Trial, prices: pd.Series) -> float:
            """
            Objective function for Optuna to maximize.
            """
            params = {
                "fast_window": trial.suggest_int("fast_window", 10, 50),
                "slow_window": trial.suggest_int("slow_window", 51, 200),
                "stop_loss": trial.suggest_float("stop_loss", 0.05, 0.30),
                "take_profit": trial.suggest_float("take_profit", 0.10, 0.50),
            }

            # Ensure fast_window is smaller than slow_window
            if params["fast_window"] >= params["slow_window"]:
                return -1.0  # Return a poor score to prune this trial

            portfolio = run_backtest(prices, params)
            return portfolio.total_return()

        logger.info(f"Running Optuna optimization for {N_TRIALS} trials...")
        study = optuna.create_study(
            direction="maximize", pruner=optuna.pruners.MedianPruner()
        )
        objective_with_data = functools.partial(objective, prices=train_prices)
        study.optimize(
            objective_with_data,
            n_trials=N_TRIALS,
            n_jobs=-1,
        )  # Use all available CPU cores

        best_params = study.best_params
        latest_best_params = best_params
        logger.info(f"Optimization complete. Best Return: {study.best_value:.2%}")
        logger.info(f"Best Parameters: {best_params}")

        # --- Validation Step ---
        logger.info("Validating parameters on out-of-sample test data...")
        test_portfolio = run_backtest(test_prices, best_params)
        fold_return = test_portfolio.total_return()
        fold_results.append(fold_return)

        logger.info(f"Fold {i+1} Out-of-Sample Return: {fold_return:.2%}")
        logger.info(f"Total Trades: {test_portfolio.trades.count()}")

    # --- Save latest parameters for the Flywheel Effect ---
    if latest_best_params:
        logger.info("--- Saving latest optimal parameters for live bot ---")
        # These are the parameters found on the most recent training data
        with open(PARAMS_FILE, "w") as f:
            json.dump(latest_best_params, f, indent=2)
        logger.info(f"Saved parameters to {PARAMS_FILE}")

    # --- Final Report ---
    total_return = np.prod([1 + r for r in fold_results]) - 1
    logger.info("--- WFO Final Results ---")
    logger.info(f"Analyzed {N_FOLDS} folds.")
    logger.info(f"Total Out-of-Sample Return: {total_return:.2%}")
    logger.info(f"Average Fold Return: {np.mean(fold_results):.2%}")


if __name__ == "__main__":
    # Suppress Optuna's informational messages
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    try:
        prices = load_price_data(TARGET_SYMBOL)
        run_wfo(prices)
    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Error: {e}", exc_info=True)
        logger.error(
            "Please ensure 'data_access/data/coins.json' exists and contains "
            f"historical data for the symbol '{TARGET_SYMBOL}'."
        )
        logger.error("You can generate it by running the main bot once.")
        sys.exit(1)
    except Exception:
        logger.critical("An unexpected error occurred.", exc_info=True)
        sys.exit(1)
