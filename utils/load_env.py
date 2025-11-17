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
    engine_module: str
    engine_class: str
    evaluator_module: str
    evaluator_class: str
    evaluator_version: str
    strategy_module: str
    strategy_class: str
    strategy_version: str
    shadow_mode_enabled: bool
    shadow_evaluator_module: Optional[str]
    shadow_evaluator_class: Optional[str]
    shadow_strategy_module: Optional[str]
    shadow_strategy_class: Optional[str]
    coingecko_enabled: bool
    binance_enabled: bool


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
        engine_module=os.getenv("ENGINE_MODULE", "domain.engine"),
        engine_class=os.getenv("ENGINE_CLASS", "Engine"),
        evaluator_module=os.getenv("EVALUATOR_MODULE", "domain.evaluator"),
        evaluator_class=os.getenv("EVALUATOR_CLASS", "Evaluator"),
        evaluator_version=os.getenv("EVALUATOR_VERSION", "v1"),
        strategy_module=os.getenv("STRATEGY_MODULE", "domain.strategy"),
        strategy_class=os.getenv("STRATEGY_CLASS", "Strategy"),
        strategy_version=os.getenv("STRATEGY_VERSION", "v1"),
        shadow_mode_enabled=os.getenv("SHADOW_MODE_ENABLED", "False").lower() == "true",
        shadow_evaluator_module=os.getenv("SHADOW_EVALUATOR_MODULE"),
        shadow_evaluator_class=os.getenv("SHADOW_EVALUATOR_CLASS"),
        shadow_strategy_module=os.getenv("SHADOW_STRATEGY_MODULE"),
        shadow_strategy_class=os.getenv("SHADOW_STRATEGY_CLASS"),
        coingecko_enabled=os.getenv("COINGECKO_ENABLED", "True").lower() == "true",
        binance_enabled=os.getenv("BINANCE_ENABLED", "False").lower() == "true",
    )
    return settings


# Create a single, globally-used settings object
settings = load_settings()

__all__ = ["settings", "Settings", "TradeSettings", "PoolSafetySettings"]
