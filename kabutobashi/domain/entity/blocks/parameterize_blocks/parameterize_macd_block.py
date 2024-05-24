from dataclasses import dataclass

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..abc_block import BlockGlue, IBlockInput, IBlockOutput
from ..decorator import block
from .abc_parameterize_block import get_impact


@dataclass(frozen=True)
class ParameterizeMacdBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        processed_macd_series = block_glue.block_outputs["process_macd"].series
        if processed_macd_series is None:
            raise KabutobashiBlockSeriesIsNoneError()

        return ParameterizeMacdBlockInput(series=processed_macd_series, params=block_glue.params)

    def _validate(self):
        if self.series is not None:
            columns = self.series.columns
            assert "signal" in columns, "ParameterizeMacdBlockInput must have 'signal' column"
            assert "histogram" in columns, "ParameterizeMacdBlockInput must have 'histogram' column"


@dataclass(frozen=True)
class ParameterizeMacdBlockOutput(IBlockOutput):
    block_name: str = "parameterize_macd"

    def _validate(self):
        keys = self.params.keys()
        assert "signal" in keys, "ParameterizeMacdBlockOutput must have 'signal' column"
        assert "histogram" in keys, "ParameterizeMacdBlockOutput must have 'histogram' column"
        assert "macd_impact" in keys, "ParameterizeMacdBlockOutput must have 'macd_impact' column"


@block(block_name="parameterize_macd", pre_condition_block_name="process_macd")
class ParameterizeMacdBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "signal": df["signal"].tail(3).mean(),
            "histogram": df["histogram"].tail(3).mean(),
            "macd_impact": get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return params
