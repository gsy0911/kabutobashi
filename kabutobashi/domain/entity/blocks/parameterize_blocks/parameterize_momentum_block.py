from dataclasses import dataclass

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..abc_block import BlockGlue, IBlockInput, IBlockOutput
from ..decorator import block
from .abc_parameterize_block import get_impact


@dataclass(frozen=True)
class ParameterizeMomentumBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        initial_series = block_glue.series
        if initial_series is None:
            raise KabutobashiBlockSeriesIsNoneError()
        processed_momentum_series = block_glue.block_outputs["process_momentum"].series
        if processed_momentum_series is None:
            raise KabutobashiBlockSeriesIsNoneError()

        return ParameterizeMomentumBlockInput(series=processed_momentum_series.join(initial_series["close"]), params={})

    def _validate(self):
        if self.series is not None:
            columns = self.series.columns
            assert "buy_signal" in columns, "ParameterizeMomentumBlockInput must have 'buy_signal' column"
            assert "sell_signal" in columns, "ParameterizeMomentumBlockInput must have 'sell_signal' column"


@dataclass(frozen=True)
class ParameterizeMomentumBlockOutput(IBlockOutput):
    block_name: str = "parameterize_momentum"

    def _validate(self):
        keys = self.params.keys()
        assert "momentum_impact" in keys, "ParameterizeMomentumBlockOutput must have 'momentum_impact' column"


@block(block_name="parameterize_momentum", pre_condition_block_name="process_momentum")
class ParameterizeMomentumBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "momentum_impact": get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return params
