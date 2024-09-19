CREATE DATABASE IF NOT EXISTS bitcoin_data;

USE bitcoin_data;

CREATE TABLE IF NOT EXISTS bitcoin_prices (
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    buy_price FLOAT NOT NULL,
    sell_price FLOAT NOT NULL,
    volume FLOAT NOT NULL
);
