import pandas as pd

from kabutobashi.infrastructure.repository import KabutobashiDatabase

from ..decorator import block


@block(
    block_name="write_sqlite3",
    series_required_columns=["code", "dt", "name", "open", "close", "high", "low", "volume", "per", "psr", "pbr"],
    series_required_columns_mode="all",
)
class WriteStockSqlite3Block:
    series: pd.DataFrame

    def _process(self) -> dict:
        KabutobashiDatabase().insert_stock_df(df=self.series)
        return {"status": "success"}
