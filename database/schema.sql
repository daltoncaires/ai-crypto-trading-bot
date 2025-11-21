CREATE TABLE coins (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    coin_id VARCHAR(50) UNIQUE NOT NULL,
    realized_pnl REAL DEFAULT 0.0,
    price_change REAL DEFAULT 0.0
);

CREATE TABLE prices (
    id SERIAL PRIMARY KEY,
    coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    timestamp BIGINT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    buy_price REAL NOT NULL,
    quantity REAL NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    direction VARCHAR(4) NOT NULL
);

CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    cost_basis REAL NOT NULL,
    total_quantity REAL NOT NULL
);

CREATE TABLE pnl_entries (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolio(id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    value REAL NOT NULL
);
