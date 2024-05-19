from dataclasses import dataclass

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockParamsIsNoneError, KabutobashiBlockSeriesIsNoneError

from ..abc_block import BlockGlue
from ..decorator import block
from .abc_pre_process_block import IPreProcessBlockInput, IPreProcessBlockOutput


@dataclass(frozen=True)
class DefaultPreProcessBlockInput(IPreProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        params = block_glue.params.get("default_pre_process", {})
        return cls(
            series=block_glue.series,
            params={"for_analysis": params.get("for_analysis", False)},
        )

    def _validate(self):
        pass


@dataclass(frozen=True)
class DefaultPreProcessBlockOutput(IPreProcessBlockOutput):
    block_name: str = "default_pre_process"

    def _validate(self):
        pass


@block(block_name="default_pre_process", pre_condition_block_name="extract_stock_info")
class DefaultPreProcessBlock:
    for_analysis: bool
    series: pd.DataFrame

    def _process(self) -> pd.DataFrame:

        df = self.series
        if self.for_analysis:
            required_cols = ["open", "high", "low", "close", "code", "volume"]
            if df is None:
                raise KabutobashiBlockSeriesIsNoneError()
            df = df[required_cols]
        return df
