"""Environment helpers and strongly typed configuration objects."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class TradeSettings:
    """Runtime configuration that controls trading decisions."""

    take_profit: float
    stop_loss: float
    order_amount: float
    price_change_threshold: float


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


def _read_env_float(var_name: str) -> float:
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' is required")
    return float(value)


def _load_prompt_template(path: Optional[str]) -> str:
    if not path:
        raise ValueError("Environment variable 'PROMPT_TEMPLATE' is required")
    template_path = Path(path)
    if not template_path.exists():
        raise FileNotFoundError(
            f"Prompt template file '{template_path}' does not exist"
        )
    return template_path.read_text()


settings = Settings(
    cg_api_key=os.getenv("CG_API_KEY", ""),
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    prompt_template=_load_prompt_template(os.getenv("PROMPT_TEMPLATE")),
    trade=TradeSettings(
        take_profit=_read_env_float("TAKE_PROFIT"),
        stop_loss=_read_env_float("STOP_LOSS"),
        order_amount=_read_env_float("ORDER_AMOUNT"),
        price_change_threshold=_read_env_float("PRICE_CHANGE"),
    ),
    pool=PoolSafetySettings(
        min_volume_24h=_read_env_float("MIN_VOLUME_24H"),
        min_reserves_usd=_read_env_float("MIN_RESERVES_USD"),
        min_buys_24h=_read_env_float("MIN_BUYS_24H"),
    ),
)

__all__ = ["settings", "Settings", "TradeSettings", "PoolSafetySettings"]
