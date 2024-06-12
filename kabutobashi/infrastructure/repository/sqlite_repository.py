import os
import sqlite3

import pandas as pd

PARENT_PATH = os.path.abspath(os.path.dirname(__file__))
SOURCE_PATH = os.path.abspath(os.path.dirname(PARENT_PATH))


class KabutobashiDatabase:
    def __init__(self, database_dir: str = SOURCE_PATH, database_name: str = "kabutobashi.db"):
        self.database_dir = database_dir
        self.database_name = database_name
        self.con = None

    def __enter__(self):
        self.con = sqlite3.connect(f"{self.database_dir}/{self.database_name}")
        return self.con

    def __exit__(self, ex_type, ex_value, trace):
        self.con.commit()
        self.con.close()

    def initialize(self):
        create_statement = """
            CREATE TABLE IF NOT EXISTS stock(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code INTEGER,
                dt TEXT,
                name TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                per REAL,
                psr REAL,
                pbr REAL)
            """
        create_index_statement = "CREATE INDEX stock_code_dt_idx ON stock (code, dt)"
        with self as conn:
            cur = conn.cursor()
            cur.execute(create_statement)
            cur.execute(create_index_statement)

    def insert_stock_df(self, df: pd.DataFrame):
        stock_table_columns = ["code", "dt", "name", "open", "close", "high", "low", "per", "psr", "pbr"]
        stock_table_name = "stock"
        with self as conn:
            df[stock_table_columns].to_sql(stock_table_name, conn, if_exists="replace")
