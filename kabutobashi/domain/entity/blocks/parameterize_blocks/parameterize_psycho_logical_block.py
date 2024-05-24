from dataclasses import dataclass

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..abc_block import BlockGlue, IBlockInput, IBlockOutput
from ..decorator import block
from .abc_parameterize_block import get_impact


@dataclass(frozen=True)
class ParameterizePsychoLogicalBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        initial_series = block_glue.series
        if initial_series is None:
            raise KabutobashiBlockSeriesIsNoneError()
        processed_psycho_logical_series = block_glue.block_outputs["process_psycho_logical"].series
        if processed_psycho_logical_series is None:
            raise KabutobashiBlockSeriesIsNoneError()

        return ParameterizePsychoLogicalBlockInput(
            series=processed_psycho_logical_series.join(initial_series["close"]), params={}
        )

    def _validate(self):
        if self.series is not None:
            columns = self.series.columns
            assert "psycho_line" in columns, "ParameterizePsychoLogicalBlockInput must have 'psycho_line' column"


@dataclass(frozen=True)
class ParameterizePsychoLogicalBlockOutput(IBlockOutput):
    block_name: str = "parameterize_psycho_logical"

    def _validate(self):
        keys = self.params.keys()
        assert "psycho_line" in keys, "ParameterizePsychoLogicalBlockOutput must have 'psycho_line' column"
        assert (
            "psycho_logical_impact" in keys
        ), "ParameterizePsychoLogicalBlockOutput must have 'psycho_logical_impact' column"


@block(block_name="parameterize_psycho_logical", pre_condition_block_name="process_psycho_logical")
class ParameterizePsychoLogicalBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "psycho_line": df["psycho_line"].tail(3).mean(),
            "psycho_logical_impact": get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return params
