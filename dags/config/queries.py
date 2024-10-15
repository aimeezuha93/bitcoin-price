query_schema = "CREATE SCHEMA IF NOT EXISTS bitcoin;"

query_table = """
    CREATE TABLE IF NOT EXISTS bitcoin.quarter_prices(
        date VARCHAR,
        price NUMERIC
    );
"""

query_table_avg = """
    CREATE TABLE IF NOT EXISTS bitcoin.moving_average(
        date TIMESTAMP,
        price NUMERIC,
        moving_average NUMERIC
    );
"""
