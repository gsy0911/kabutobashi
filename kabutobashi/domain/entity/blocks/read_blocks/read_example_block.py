import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue, IBlockInput, IBlockOutput
from .abc_read_block import IReadBlock, IReadBlockInput

PARENT_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_ROOT = Path(PARENT_PATH).parent.parent.parent.parent.parent
DATA_PATH = f"{PACKAGE_ROOT}/data"


@dataclass(frozen=True)
class ReadExampleBlockInput(IReadBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        input_params = block_glue.params.get("read_example", {})
        code = input_params.get("code")
        return cls(
            series=block_glue.series,
            params={
                "code": code,
            },
        )

    def _validate(self):
        if self.params:
            keys = self.params.keys()
            assert "code" in keys, "ReadExampleBlockInput must have 'code' column"


@dataclass(frozen=True)
class ReadExampleBlockOutput(IBlockOutput):
    block_name: str = "read_example"

    def _validate(self):
        pass


@inject
@dataclass(frozen=True)
class ReadExampleBlock(IReadBlock):
    def _process(self) -> ReadExampleBlockOutput:
        if not isinstance(self.block_input, ReadExampleBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        file_name = "example.csv.gz"
        df = pd.read_csv(f"{DATA_PATH}/{file_name}")
        df = df[df["code"] == self.block_input.params["code"]]
        df.index = df["dt"]
        return ReadExampleBlockOutput.of(series=df, params=self.block_input.params)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IReadBlockInput, to=ReadExampleBlockInput)
