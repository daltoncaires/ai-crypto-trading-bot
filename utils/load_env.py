"""Environment helpers and strongly typed configuration objects."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

PARAMS_FILE = "best_params.json"


@dataclass(frozen=True)
class TradeSettings:
    """Runtime configuration that controls trading decisions."""

    take_profit: float
    stop_loss: float
    order_amount: float
    price_change_threshold: float
    # Parameters for the optimizer's placeholder strategy
    fast_window: Optional[int] = None
    slow_window: Optional[int] = None


@dataclass(frozen=True)
class PoolSafetySettings:
    """Thresholds used to filter CoinGecko pool data."""

    min_volume_24h: float
    min_reserves_usd: float
    min_buys_24h: float


@dataclass(frozen=True)
class Settings:
    """Top-level settings container shared across the application."""

    cg_api_key: str
    openai_api_key: str
    prompt_template: str
    trade: TradeSettings
    pool: PoolSafetySettings


def _read_env_float(var_name: str, default: Optional[float] = None) -> float:
    value = os.getenv(var_name)
    if value is None:
        if default is not None:
            return default
        raise ValueError(f"Environment variable '{var_name}' is required")
    return float(value)


def _load_prompt_template(path: Optional[str]) -> str:
    """
    Loads the prompt template from the given path. If the path is not
    provided or the file doesn't exist, it returns a default prompt.
    """
    default_prompt = (
        "Given the following crypto data, should I BUY, SELL, or HOLD? "
        "Provide a brief justification for your decision. "
        "Context: {context}"
    )
    if not path:
        print("--- PROMPT_TEMPLATE env var not set, using default prompt. ---")
        return default_prompt
    template_path = Path(path)
    if not template_path.exists():
        print(
            f"--- Prompt template file '{path}' not found, using default prompt. ---"
        )
        return default_prompt
    return template_path.read_text()


def load_settings() -> Settings:
    """
    Loads settings from the .env file and overrides them with dynamically
    optimized parameters if they exist (Flywheel Effect).
    """
    # 1. Load base settings from .env file
    trade_settings = TradeSettings(
        take_profit=_read_env_float("TAKE_PROFIT"),
        stop_loss=_read_env_float("STOP_LOSS"),
        order_amount=_read_env_float("ORDER_AMOUNT"),
        price_change_threshold=_read_env_float("PRICE_CHANGE"),
        fast_window=int(_read_env_float("FAST_WINDOW", 21)),
        slow_window=int(_read_env_float("SLOW_WINDOW", 50)),
    )

    # 2. Check for and apply optimized parameters
    if Path(PARAMS_FILE).exists():
        print(f"--- Found '{PARAMS_FILE}', applying optimized parameters. ---")
        with open(PARAMS_FILE, "r") as f:
            optimized_params = json.load(f)

        # Create a new TradeSettings instance with overridden values
        # The `replace` function from dataclasses is perfect for this
        trade_settings = replace(trade_settings, **optimized_params)
        print(f"--- Overridden trade settings: {trade_settings} ---")

    # 3. Load other settings and assemble the final config
    settings = Settings(
        cg_api_key=os.getenv("CG_API_KEY", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        prompt_template=_load_prompt_template(os.getenv("PROMPT_TEMPLATE")),
        trade=trade_settings,
        pool=PoolSafetySettings(
            min_volume_24h=_read_env_float("MIN_VOLUME_24H"),
            min_reserves_usd=_read_env_float("MIN_RESERVES_USD"),
            min_buys_24h=_read_env_float("MIN_BUYS_24H"),
        ),
    )
    return settings


# Create a single, globally-used settings object
settings = load_settings()

__all__ = ["settings", "Settings", "TradeSettings", "PoolSafetySettings"]
