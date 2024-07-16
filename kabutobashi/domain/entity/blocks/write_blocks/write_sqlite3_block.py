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
