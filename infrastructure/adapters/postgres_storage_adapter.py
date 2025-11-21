"""
PostgreSQL adapter for data storage services.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from domain.models.coin import Coin
from domain.models.paper_order import PaperOrder
from domain.models.portfolio_item import PnLEntry, PortfolioItem
from domain.ports.data_storage_port import DataStoragePort
from utils.load_env import DBSettings
from utils.logger import get_logger

logger = get_logger(__name__)


class PostgreSQLStorageAdapter(DataStoragePort):
    """
    A concrete implementation of DataStoragePort for PostgreSQL.
    """

    def __init__(self, db_settings: DBSettings):
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=db_settings.max_pool_connections,
            host=db_settings.host,
            port=db_settings.port,
            user=db_settings.user,
            password=db_settings.password,
            dbname=db_settings.dbname,
        )
        self.initialize_database()
        logger.info("PostgreSQLStorageAdapter initialized.")

    def initialize_database(self):
        """
        Initializes the database by creating the tables from the schema.sql file.
        """
        with self.pool.getconn() as conn:
            with conn.cursor() as cur:
                try:
                    with open("database/schema.sql", "r") as f:
                        cur.execute(f.read())
                    conn.commit()
                    logger.info("Database initialized successfully.")
                except psycopg2.Error as e:
                    logger.error(f"Error initializing database: {e}")
                    conn.rollback()
                finally:
                    self.pool.putconn(conn)

    def get_all_coins(self) -> List[Coin]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute("SELECT * FROM coins;")
                    coins_data = cur.fetchall()
                    return [Coin(**data) for data in coins_data]
                except psycopg2.Error as e:
                    logger.error(f"Error getting all coins: {e}")
                    return []
                finally:
                    self.pool.putconn(conn)

    def get_coin_by_symbol(self, symbol: str) -> Optional[Coin]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute("SELECT * FROM coins WHERE symbol = %s;", (symbol,))
                    coin_data = cur.fetchone()
                    if coin_data:
                        return Coin(**coin_data)
                    return None
                except psycopg2.Error as e:
                    logger.error(f"Error getting coin {symbol}: {e}")
                    return None
                finally:
                    self.pool.putconn(conn)

    def add_coin(
        self,
        symbol: str,
        coin_id: str,
        realized_pnl: float = 0.0,
        price_change: float = 0.0,
    ) -> Optional[Coin]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(
                        """
                        INSERT INTO coins (symbol, coin_id, realized_pnl, price_change)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *;
                        """,
                        (symbol, coin_id, realized_pnl, price_change),
                    )
                    new_coin_data = cur.fetchone()
                    conn.commit()
                    return Coin(**new_coin_data)
                except psycopg2.Error as e:
                    logger.error(f"Error adding coin {symbol}: {e}")
                    conn.rollback()
                    return None
                finally:
                    self.pool.putconn(conn)

    def add_prices_to_coin(
        self, symbol: str, prices: List[list]
    ) -> Optional[List[list]]:
        coin = self.get_coin_by_symbol(symbol)
        if not coin:
            return None

        with self.pool.getconn() as conn:
            with conn.cursor() as cur:
                try:
                    args_list = [
                        (coin.id, p[0], p[1], p[2], p[3], p[4]) for p in prices
                    ]
                    psycopg2.extras.execute_values(
                        cur,
                        """
                        INSERT INTO prices (coin_id, timestamp, open, high, low, close)
                        VALUES %s;
                        """,
                        args_list,
                    )
                    conn.commit()
                    return prices
                except psycopg2.Error as e:
                    logger.error(f"Error adding prices to coin {symbol}: {e}")
                    conn.rollback()
                    return None
                finally:
                    self.pool.putconn(conn)

    def update_coin_price_change(
        self, symbol: str, price_change: float
    ) -> Optional[Coin]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(
                        """
                        UPDATE coins
                        SET price_change = %s
                        WHERE symbol = %s
                        RETURNING *;
                        """,
                        (price_change, symbol),
                    )
                    updated_coin_data = cur.fetchone()
                    conn.commit()
                    if updated_coin_data:
                        return Coin(**updated_coin_data)
                    return None
                except psycopg2.Error as e:
                    logger.error(f"Error updating price change for coin {symbol}: {e}")
                    conn.rollback()
                    return None
                finally:
                    self.pool.putconn(conn)

    def update_coin_pnl(self, symbol: str, new_realized_pnl: float) -> Optional[Coin]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(
                        """
                        UPDATE coins
                        SET realized_pnl = %s
                        WHERE symbol = %s
                        RETURNING *;
                        """,
                        (new_realized_pnl, symbol),
                    )
                    updated_coin_data = cur.fetchone()
                    conn.commit()
                    if updated_coin_data:
                        return Coin(**updated_coin_data)
                    return None
                except psycopg2.Error as e:
                    logger.error(f"Error updating PNL for coin {symbol}: {e}")
                    conn.rollback()
                    return None
                finally:
                    self.pool.putconn(conn)

    def get_all_orders(
        self, direction: Optional[Literal["BUY", "SELL"]] = None
    ) -> List[PaperOrder]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    if direction:
                        cur.execute("SELECT * FROM orders WHERE direction = %s;", (direction,))
                    else:
                        cur.execute("SELECT * FROM orders;")
                    orders_data = cur.fetchall()
                    return [PaperOrder(**data) for data in orders_data]
                except psycopg2.Error as e:
                    logger.error(f"Error getting all orders: {e}")
                    return []
                finally:
                    self.pool.putconn(conn)

    def insert_order(
        self,
        timestamp: datetime,
        buy_price: float,
        quantity: float,
        symbol: str,
        direction: str,
    ) -> Optional[PaperOrder]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(
                        """
                        INSERT INTO orders (timestamp, buy_price, quantity, symbol, direction)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *;
                        """,
                        (timestamp, buy_price, quantity, symbol, direction),
                    )
                    new_order_data = cur.fetchone()
                    conn.commit()
                    return PaperOrder(**new_order_data)
                except psycopg2.Error as e:
                    logger.error(f"Error inserting order for {symbol}: {e}")
                    conn.rollback()
                    return None
                finally:
                    self.pool.putconn(conn)

    def get_all_portfolio_items(self) -> List[PortfolioItem]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute("SELECT * FROM portfolio;")
                    portfolio_data = cur.fetchall()
                    return [PortfolioItem(**data) for data in portfolio_data]
                except psycopg2.Error as e:
                    logger.error(f"Error getting all portfolio items: {e}")
                    return []
                finally:
                    self.pool.putconn(conn)

    def get_portfolio_item_by_symbol(self, symbol: str) -> Optional[PortfolioItem]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute("SELECT * FROM portfolio WHERE symbol = %s;", (symbol,))
                    item_data = cur.fetchone()
                    if item_data:
                        return PortfolioItem(**item_data)
                    return None
                except psycopg2.Error as e:
                    logger.error(f"Error getting portfolio item {symbol}: {e}")
                    return None
                finally:
                    self.pool.putconn(conn)

    def insert_portfolio_item(
        self, symbol: str, cost_basis: float, total_quantity: float
    ) -> Optional[PortfolioItem]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(
                        """
                        INSERT INTO portfolio (symbol, cost_basis, total_quantity)
                        VALUES (%s, %s, %s)
                        RETURNING *;
                        """,
                        (symbol, cost_basis, total_quantity),
                    )
                    new_item_data = cur.fetchone()
                    conn.commit()
                    return PortfolioItem(**new_item_data)
                except psycopg2.Error as e:
                    logger.error(f"Error inserting portfolio item for {symbol}: {e}")
                    conn.rollback()
                    return None
                finally:
                    self.pool.putconn(conn)

    def update_portfolio_item_by_symbol(
        self, symbol: str, cost_basis: float, additional_quantity: float
    ) -> Optional[PortfolioItem]:
        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(
                        """
                        UPDATE portfolio
                        SET cost_basis = %s, total_quantity = total_quantity + %s
                        WHERE symbol = %s
                        RETURNING *;
                        """,
                        (cost_basis, additional_quantity, symbol),
                    )
                    updated_item_data = cur.fetchone()
                    conn.commit()
                    if updated_item_data:
                        return PortfolioItem(**updated_item_data)
                    return None
                except psycopg2.Error as e:
                    logger.error(f"Error updating portfolio item for {symbol}: {e}")
                    conn.rollback()
                    return None
                finally:
                    self.pool.putconn(conn)

    def add_pnl_entry_by_symbol(
        self, symbol: str, date: datetime, value: float
    ) -> Optional[PnLEntry]:
        portfolio_item = self.get_portfolio_item_by_symbol(symbol)
        if not portfolio_item:
            return None

        with self.pool.getconn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(
                        """
                        INSERT INTO pnl_entries (portfolio_id, date, value)
                        VALUES (%s, %s, %s)
                        RETURNING *;
                        """,
                        (portfolio_item.id, date, value),
                    )
                    new_pnl_entry_data = cur.fetchone()
                    conn.commit()
                    return PnLEntry(**new_pnl_entry_data)
                except psycopg2.Error as e:
                    logger.error(f"Error adding PNL entry for {symbol}: {e}")
                    conn.rollback()
                    return None
                finally:
                    self.pool.putconn(conn)
