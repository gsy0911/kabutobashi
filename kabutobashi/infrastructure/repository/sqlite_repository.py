import sqlite3
from logging import INFO, getLogger
from pathlib import Path
from typing import Optional

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
        # stock daily record
        drop_stock_table = "DROP TABLE IF EXISTS stock"
        create_stock_statement = """
            CREATE TABLE IF NOT EXISTS stock(
                code TEXT NOT NULL,
                dt TEXT NOT NULL,
                name TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                PRIMARY KEY (code, dt)
            )
            """
        create_stock_index_statement = "CREATE INDEX IF NOT EXISTS stock_code_dt_idx ON stock (code, dt)"

        # evaluate
        drop_impact_table = "DROP TABLE IF EXISTS impact"
        create_impact_statement = """
            CREATE TABLE IF NOT EXISTS impact(
                code TEXT NOT NULL,
                dt TEXT NOT NULL,
                impact REAL,
                PRIMARY KEY (code, dt)
            )
            """
        create_impact_index_statement = "CREATE INDEX IF NOT EXISTS impact_code_dt_idx ON impact (code, dt)"

        # brand
        drop_brand_table = "DROP TABLE IF EXISTS brand"
        create_brand_statement = """
            CREATE TABLE IF NOT EXISTS brand(
                code TEXT NOT NULL,
                name TEXT,
                market TEXT,
                industry_type TEXT,
                PRIMARY KEY (code)
            )
            """
        create_brand_index_statement = "CREATE INDEX IF NOT EXISTS brand_code_dt_idx ON brand (code)"
        with self as conn:
            cur = conn.cursor()
            cur.execute(drop_stock_table)
            cur.execute(create_stock_statement)
            cur.execute(create_stock_index_statement)
            cur.execute(drop_impact_table)
            cur.execute(create_impact_statement)
            cur.execute(create_impact_index_statement)
            cur.execute(drop_brand_table)
            cur.execute(create_brand_statement)
            cur.execute(create_brand_index_statement)
        return self

    def insert_stock_df(self, df: pd.DataFrame) -> "KabutobashiDatabase":
        stock_table_columns = ["code", "dt", "name", "open", "close", "high", "low", "volume"]
        stock_table_name = "stock"
        with self as conn:
            df = df.reset_index(drop=True)
            try:
                df[stock_table_columns].to_sql(stock_table_name, conn, if_exists="append", index=False)
            except sqlite3.IntegrityError:
                logger.warning(f"stock_df(stock.code, stock.dt) already exists, {df=}")
        return self

    def select_stock_df(self, code: str):
        stock_table_columns = ["code", "dt", "name", "open", "close", "high", "low", "volume"]
        with self as conn:
            df = pd.read_sql(f"SELECT * FROM stock WHERE code = '{code}'", conn)
            return df[stock_table_columns]

    def insert_impact_df(self, df: pd.DataFrame) -> "KabutobashiDatabase":
        impact_table_columns = ["code", "dt", "impact"]
        stock_table_name = "impact"
        with self as conn:
            df = df.reset_index(drop=True)
            try:
                df[impact_table_columns].to_sql(stock_table_name, conn, if_exists="append", index=False)
            except sqlite3.IntegrityError:
                logger.warning(f"impact_df(stock.code, stock.dt) already exists")
        return self

    def select_impact_df(self, dt: str) -> Optional[pd.DataFrame]:
        impact_table_columns = ["code", "dt", "impact"]
        with self as conn:
            try:
                df = pd.read_sql(f"SELECT * FROM impact WHERE dt = '{dt}' ORDER BY impact", conn)
                df["dt"] = df["dt"].astype(str)
                return df[impact_table_columns]
            except sqlite3.DatabaseError:
                return None

    def insert_brand_df(self, df: pd.DataFrame) -> "KabutobashiDatabase":
        impact_table_columns = ["code", "name", "market", "industry_type"]
        stock_table_name = "brand"
        with self as conn:
            df = df.reset_index(drop=True)
            try:
                df[impact_table_columns].to_sql(stock_table_name, conn, if_exists="append", index=False)
            except sqlite3.IntegrityError:
                logger.warning(f"brand_df(brand.code) already exists")
        return self

    def select_brand_df(self) -> Optional[pd.DataFrame]:
        impact_table_columns = ["code", "name", "market", "industry_type"]
        with self as conn:
            try:
                df = pd.read_sql(f"SELECT * FROM brand ORDER BY code", conn)
                return df[impact_table_columns]
            except sqlite3.DatabaseError:
                return None
