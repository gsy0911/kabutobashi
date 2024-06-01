import os
from pathlib import Path
from typing import Tuple

import pandas as pd

from ..decorator import block

PARENT_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_ROOT = Path(PARENT_PATH).parent.parent.parent.parent.parent
DATA_PATH = f"{PACKAGE_ROOT}/data"


@block(block_name="read_example")
class ReadExampleBlock:
    code: str | int

    def _process(self) -> Tuple[pd.DataFrame, dict]:
        file_name = "example.csv.gz"
        df = pd.read_csv(f"{DATA_PATH}/{file_name}")
        df = df[df["code"] == self.code]
        df.index = df["dt"]
        return df, {"code": self.code}

    def _validate_code(self, code: str | int):
        if code is None:
            raise ValueError()
