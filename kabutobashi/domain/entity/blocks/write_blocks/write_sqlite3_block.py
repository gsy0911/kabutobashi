import pandas as pd

from kabutobashi.infrastructure.repository import KabutobashiDatabase

from ..decorator import block


@block(
    block_name="write_stock_sqlite3",
    series_required_columns=["code", "dt", "name", "open", "close", "high", "low", "volume"],
    series_required_columns_mode="all",
    params_required_keys=["database_dir"],
)
class WriteStockSqlite3Block:
    series: pd.DataFrame
    database_dir: str

    def _process(self) -> dict:
        KabutobashiDatabase(database_dir=self.database_dir).insert_stock_df(df=self.series)
        return {"status": "success"}


@block(
    block_name="write_impact_sqlite3",
    series_required_columns=["code", "dt", "impact"],
    series_required_columns_mode="strict",
    params_required_keys=["database_dir"],
)
class WriteImpactSqlite3Block:
    series: pd.DataFrame
    database_dir: str

    def _process(self) -> dict:
        KabutobashiDatabase(database_dir=self.database_dir).insert_impact_df(df=self.series)
        return {"status": "success"}


@block(
    block_name="write_brand_sqlite3",
    series_required_columns=["code", "name", "market", "industry_type"],
    series_required_columns_mode="strict",
    params_required_keys=["database_dir"],
)
class WriteBrandSqlite3Block:
    series: pd.DataFrame
    database_dir: str

    def _process(self) -> dict:
        db = KabutobashiDatabase(database_dir=self.database_dir)
        current_brand_df = db.select_brand_df()
        current_code_list = current_brand_df["code"].to_list()
        insert_candidate_series = self.series[~self.series["code"].isin(current_code_list)]
        if not insert_candidate_series.empty:
            db.insert_brand_df(df=insert_candidate_series)
        return {"status": "success"}
