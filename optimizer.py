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

import json
import numpy as np
import pandas as pd
import vectorbt as vbt
import optuna

from data_access.DAL.coins_DAL import CoinsDAL

# --- Configuration ---
PARAMS_FILE = "best_params.json"
COINS_FILE = "data_access/data/coins.json"
TARGET_SYMBOL = "btc"  # Symbol to optimize for
TRANSACTION_FEES = 0.001  # Binance VIP level 0 taker fee is 0.1%

# WFO Configuration
N_FOLDS = 5  # Number of walk-forward folds
TRAIN_TEST_SPLIT = 0.7  # 70% for training, 30% for testing in each fold
N_TRIALS = 100  # Number of optimization trials for Optuna in each fold


def load_price_data(symbol: str) -> pd.Series:
    """
    Loads historical price data for a single coin from the JSON data store
    and returns it as a pandas Series.
    """
    print(f"Loading historical data for {symbol}...")
    coins_dal = CoinsDAL(COINS_FILE)
    coin = coins_dal.get_coin_by_symbol(symbol)
    if not coin or not coin.prices:
        raise ValueError(f"No historical data found for symbol: {symbol}")

    # Convert to DataFrame and set a proper DatetimeIndex
    df = pd.DataFrame(coin.prices, columns=["timestamp", "open", "high", "low", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.set_index("timestamp")
    df = df.sort_index()

    # vectorbt works with Series, so we'll use the closing price
    price_series = df["close"]
    print(f"Loaded {len(price_series)} data points for {symbol}.")
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
    print("\n--- Starting Walk-Forward Optimization ---")

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
        print(f"\n--- Processing Fold {i+1}/{N_FOLDS} ---")

        train_prices = price_series.iloc[train_idx]
        test_prices = price_series.iloc[test_idx]

        print(
            f"Train period: {train_prices.index[0]} to {train_prices.index[-1]} "
            f"({len(train_prices)} points)"
        )
        print(
            f"Test period:  {test_prices.index[0]} to {test_prices.index[-1]} "
            f"({len(test_prices)} points)"
        )

        # --- Optimization Step with Optuna ---
        def objective(trial: optuna.Trial) -> float:
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

            portfolio = run_backtest(train_prices, params)
            return portfolio.total_return()

        print(f"Running Optuna optimization for {N_TRIALS} trials...")
        study = optuna.create_study(
            direction="maximize", pruner=optuna.pruners.MedianPruner()
        )
        study.optimize(objective, n_trials=N_TRIALS, n_jobs=-1)  # Use all available CPU cores

        best_params = study.best_params
        latest_best_params = best_params
        print(f"Optimization complete. Best Return: {study.best_value:.2%}")
        print(f"Best Parameters: {best_params}")

        # --- Validation Step ---
        print("Validating parameters on out-of-sample test data...")
        test_portfolio = run_backtest(test_prices, best_params)
        fold_return = test_portfolio.total_return()
        fold_results.append(fold_return)

        print(f"Fold {i+1} Out-of-Sample Return: {fold_return:.2%}")
        print(f"Total Trades: {test_portfolio.trades.count()}")

    # --- Save latest parameters for the Flywheel Effect ---
    if latest_best_params:
        print("\n--- Saving latest optimal parameters for live bot ---")
        # These are the parameters found on the most recent training data
        with open(PARAMS_FILE, "w") as f:
            json.dump(latest_best_params, f, indent=2)
        print(f"Saved parameters to {PARAMS_FILE}")

    # --- Final Report ---
    total_return = np.prod([1 + r for r in fold_results]) - 1
    print("\n--- WFO Final Results ---")
    print(f"Analyzed {N_FOLDS} folds.")
    print(f"Total Out-of-Sample Return: {total_return:.2%}")
    print(f"Average Fold Return: {np.mean(fold_results):.2%}")


if __name__ == "__main__":
    # Suppress Optuna's informational messages
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    try:
        prices = load_price_data(TARGET_SYMBOL)
        run_wfo(prices)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        print(
            "Please ensure 'data_access/data/coins.json' exists and contains "
            f"historical data for the symbol '{TARGET_SYMBOL}'."
        )
        print("You can generate it by running the main bot once.")
