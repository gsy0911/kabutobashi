import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..abc_block import IBlockInput, IBlockOutput
from .abc_read_block import IReadBlock

PARENT_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_ROOT = Path(PARENT_PATH).parent.parent.parent.parent.parent
DATA_PATH = f"{PACKAGE_ROOT}/data"


@dataclass(frozen=True)
class ReadExampleBlockInput(IBlockInput):
    def _validate(self):
        keys = self.params.keys()
        assert "code" in keys, "ReadExampleBlockInput must have 'code' column"


@dataclass(frozen=True)
class ReadExampleBlockOutput(IBlockOutput):
    block_name: str = "read_example"

    def _validate(self):
        pass


class ReadExampleBlock(IReadBlock):
    def _process(self, block_input: ReadExampleBlockInput) -> IReadBlock:
        file_name = "example.csv.gz"
        df = pd.read_csv(f"{DATA_PATH}/{file_name}")
        df = df[df["code"] == 1375]
        df.index = df["dt"]
        return ReadExampleBlockOutput.of(series=df, params=block_input.params)
