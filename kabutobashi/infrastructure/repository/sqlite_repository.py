import sqlite3
from logging import INFO, getLogger
from pathlib import Path

import pandas as pd

logger = getLogger(__name__)
logger.setLevel(INFO)

ROOT_PATH = Path(__file__).parent.parent.parent.parent


class KabutobashiDatabase:
    def __init__(self, database_dir: str = ROOT_PATH, database_name: str = "kabutobashi.db"):
        self.database_dir = database_dir
        self.database_name = database_name
        self.con = None

    def __enter__(self):
        self.con = sqlite3.connect(f"{self.database_dir}/{self.database_name}")
        return self.con

    def __exit__(self, ex_type, ex_value, trace):
        self.con.commit()
        self.con.close()

    def initialize(self) -> "KabutobashiDatabase":
        create_statement = """
            CREATE TABLE IF NOT EXISTS stock(
                code INTEGER NOT NULL,
                dt TEXT NOT NULL,
                name TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                per REAL,
                psr REAL,
                pbr REAL,
                PRIMARY KEY (code, dt)
            )
            """
        create_index_statement = "CREATE INDEX IF NOT EXISTS stock_code_dt_idx ON stock (code, dt)"
        with self as conn:
            cur = conn.cursor()
            cur.execute(create_statement)
            cur.execute(create_index_statement)
        return self

    def insert_stock_df(self, df: pd.DataFrame) -> "KabutobashiDatabase":
        stock_table_columns = ["code", "dt", "name", "open", "close", "high", "low", "volume", "per", "psr", "pbr"]
        stock_table_name = "stock"
        with self as conn:
            df = df.reset_index(drop=True)
            try:
                df[stock_table_columns].to_sql(stock_table_name, conn, if_exists="append", index=False)
            except sqlite3.IntegrityError:
                logger.warning(f"Stock data (stock.code, stock.dt) already exists")
        return self

    def select_stock_df(self, code: str):
        stock_table_columns = ["code", "dt", "name", "open", "close", "high", "low", "volume", "per", "psr", "pbr"]
        with self as conn:
            df = pd.read_sql(f"SELECT * FROM stock WHERE code = {code}", conn)
            return df[stock_table_columns]
