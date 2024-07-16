from typing import Tuple

import pandas as pd

from kabutobashi.infrastructure.repository import KabutobashiDatabase

from ..decorator import block


@block(block_name="read_sqlite3")
class ReadSqlite3Block:
    code: str | int
    database_dir: str

    def _process(self) -> Tuple[pd.DataFrame, dict]:
        df = KabutobashiDatabase(database_dir=self.database_dir).select_stock_df(code=self.code)
        df.index = df["dt"]
        return df, {"code": self.code}

    def _validate_code(self, code: str | int):
        if code is None:
            raise ValueError()
