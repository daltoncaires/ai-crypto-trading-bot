"""Environment helpers and strongly typed configuration objects."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file only in development
if os.getenv("ENVIRONMENT") == "development":
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
class DBSettings:
    """Database connection settings."""

    host: str
    port: int
    user: str
    password: str
    dbname: str
    max_pool_connections: int


@dataclass(frozen=True)
class ApiSettings:
    """General settings for API interactions."""

    request_timeout: int
    rate_limit_sleep: int


@dataclass(frozen=True)
class CoinGeckoSettings:
    """Settings specific to the CoinGecko adapter."""

    api_root: str
    coins_per_page: int


@dataclass(frozen=True)
class CelerySettings:
    """Celery and Redis connection settings."""

    broker_url: str
    result_backend: str


@dataclass(frozen=True)
class Settings:
    """Top-level settings container shared across the application."""

    environment: str
    cg_api_key: Optional[str]
    coingecko: CoinGeckoSettings
    api: ApiSettings
    openai_api_key: str
    prompt_template: str
    trade: TradeSettings
    pool: PoolSafetySettings
    db: DBSettings
    celery: CelerySettings
    storage_provider: str
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
    market_data_provider: str
    binance_api_key: Optional[str]
    binance_api_secret: Optional[str]


def _get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieves a secret from environment variables.
    Returns None if the secret is not set and no default is provided.
    """
    value = os.getenv(key, default)
    if value is None and default is None:
        return None
    return value


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
    db_settings = DBSettings(
        host=_get_secret("DB_HOST", "localhost"),
        port=int(_get_secret("DB_PORT", "5432")),
        user=_get_secret("DB_USER", "user"),
        password=_get_secret("DB_PASSWORD", "password"),
        dbname=_get_secret("DB_NAME", "crypto_bot"),
        max_pool_connections=int(_get_secret("DB_MAX_POOL_CONNECTIONS", "10")),
    )

    api_settings = ApiSettings(
        request_timeout=int(_get_secret("API_REQUEST_TIMEOUT", "10")),
        rate_limit_sleep=int(_get_secret("API_RATE_LIMIT_SLEEP", "10")),
    )

    coingecko_settings = CoinGeckoSettings(
        api_root=_get_secret("CG_API_ROOT", "https://api.coingecko.com/api/v3"),
        coins_per_page=int(_get_secret("CG_COINS_PER_PAGE", "10")),
    )

    celery_settings = CelerySettings(
        broker_url=_get_secret("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        result_backend=_get_secret("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    )

    binance_api_key = _get_secret("BN_API_KEY")
    binance_api_secret = _get_secret("BN_API_SECRET")
    cg_api_key = _get_secret("CG_API_KEY")

    market_data_provider: str

    if binance_api_key and binance_api_secret:
        market_data_provider = "binance"
    elif cg_api_key:
        market_data_provider = "coingecko"
    else:
        raise ValueError(
            "No market data API keys found. Please set BN_API_KEY and BN_API_SECRET "
            "for Binance or CG_API_KEY for CoinGecko in your .env file."
        )

    settings = Settings(
        environment=os.getenv("ENVIRONMENT", "development"),
        cg_api_key=cg_api_key,
        coingecko=coingecko_settings,
        api=api_settings,
        openai_api_key=_get_secret("OPENAI_API_KEY", ""),
        prompt_template=_load_prompt_template(os.getenv("PROMPT_TEMPLATE")),
        trade=trade_settings,
        pool=PoolSafetySettings(
            min_volume_24h=_read_env_float("MIN_VOLUME_24H"),
            min_reserves_usd=_read_env_float("MIN_RESERVES_USD"),
            min_buys_24h=_read_env_float("MIN_BUYS_24H"),
        ),
        db=db_settings,
        celery=celery_settings,
        storage_provider=os.getenv("STORAGE_PROVIDER", "json"),
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
        market_data_provider=market_data_provider,
        binance_api_key=binance_api_key,
        binance_api_secret=binance_api_secret,
    )
    return settings


# Create a single, globally-used settings object
settings = load_settings()

__all__ = ["settings", "Settings", "TradeSettings", "PoolSafetySettings", "DBSettings", "CelerySettings"]
