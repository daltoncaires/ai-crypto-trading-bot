"""
Factory for creating storage adapters.
"""
from domain.ports.data_storage_port import DataStoragePort
from infrastructure.adapters.json_storage_adapter import JSONStorageAdapter
from infrastructure.adapters.postgres_storage_adapter import PostgreSQLStorageAdapter
from utils.load_env import Settings


def get_storage_adapter(settings: Settings) -> DataStoragePort:
    """
    Returns a storage adapter based on the settings.
    """
    if settings.storage_provider == "postgres":
        return PostgreSQLStorageAdapter(settings.db)
    elif settings.storage_provider == "json":
        # This is not ideal, as the JSON adapter needs file paths.
        # This will be fixed in a future step.
        return JSONStorageAdapter(
            coins_file="data/coins.json",
            orders_file="data/orders.json",
            portfolio_file="data/portfolio.json",
        )
    else:
        raise ValueError(f"Invalid storage provider: {settings.storage_provider}")
