import pandas as pd

from kabutobashi.infrastructure.repository import KabutobashiDatabase

from ..decorator import block


@block(
    block_name="write_stock_sqlite3",
    series_required_columns=["code", "dt", "name", "open", "close", "high", "low", "volume", "per", "psr", "pbr"],
    series_required_columns_mode="all",
)
class WriteStockSqlite3Block:
    series: pd.DataFrame

    def _process(self) -> dict:
        KabutobashiDatabase().insert_stock_df(df=self.series)
        return {"status": "success"}


@block(
    block_name="write_impact_sqlite3",
    series_required_columns=["code", "dt", "impact"],
    series_required_columns_mode="strict",
)
class WriteImpactSqlite3Block:
    series: pd.DataFrame

    def _process(self) -> dict:
        KabutobashiDatabase().insert_impact_df(df=self.series)
        return {"status": "success"}
