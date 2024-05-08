from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import (
    KabutobashiBlockInstanceMismatchError,
    KabutobashiBlockParamsIsNoneError,
    KabutobashiBlockSeriesIsNoneError,
)

from ..abc_block import BlockGlue, IBlockInput, IBlockOutput
from .abc_parameterize_block import IParameterizeBlock


@dataclass(frozen=True)
class ParameterizeMomentumBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        initial_series = block_glue.series
        processed_momentum_series = block_glue.block_outputs["process_momentum"].series
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


@inject
@dataclass(frozen=True)
class ParameterizeMomentumBlock(IParameterizeBlock):

    def _process(self, block_input: IBlockInput) -> ParameterizeMomentumBlockOutput:
        if not isinstance(block_input, ParameterizeMomentumBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        df = block_input.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "momentum_impact": self._get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return ParameterizeMomentumBlockOutput.of(series=None, params=params)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=ParameterizeMomentumBlockInput)
