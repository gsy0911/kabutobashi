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
class ParameterizeSmaBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        initial_series = block_glue.series
        if initial_series is None:
            raise KabutobashiBlockSeriesIsNoneError()
        processed_sma_series = block_glue.block_outputs["process_sma"].series
        if processed_sma_series is None:
            raise KabutobashiBlockSeriesIsNoneError()

        return ParameterizeSmaBlockInput(series=processed_sma_series.join(initial_series["close"]), params={})

    def _validate(self):
        if self.series is not None:
            columns = self.series.columns
            assert "close" in columns, "ParameterizeSmaBlockInput must have 'close' column"
            assert "sma_short" in columns, "ParameterizeSmaBlockInput must have 'sma_short' column"
            assert "sma_medium" in columns, "ParameterizeSmaBlockInput must have 'sma_medium' column"
            assert "sma_long" in columns, "ParameterizeSmaBlockInput must have 'sma_long' column"
            assert "buy_signal" in columns, "ParameterizeSmaBlockInput must have 'buy_signal' column"
            assert "sell_signal" in columns, "ParameterizeSmaBlockInput must have 'sell_signal' column"


@dataclass(frozen=True)
class ParameterizeSmaBlockOutput(IBlockOutput):
    block_name: str = "parameterize_sma"

    def _validate(self):
        keys = self.params.keys()
        assert "sma_short_diff" in keys, "ParameterizeSmaBlockOutput must have 'sma_short_diff' column"
        assert "sma_medium_diff" in keys, "ParameterizeSmaBlockOutput must have 'sma_medium_diff' column"
        assert "sma_long_diff" in keys, "ParameterizeSmaBlockOutput must have 'sma_long_diff' column"
        assert "sma_long_short" in keys, "ParameterizeSmaBlockOutput must have 'sma_long_short' column"
        assert "sma_long_medium" in keys, "ParameterizeSmaBlockOutput must have 'sma_long_medium' column"
        assert "sma_impact" in keys, "ParameterizeSmaBlockOutput must have 'sma_impact' column"


@inject
@dataclass(frozen=True)
class ParameterizeSmaBlock(IParameterizeBlock):

    def _process(self, block_input: IBlockInput) -> ParameterizeSmaBlockOutput:
        if not isinstance(block_input, ParameterizeSmaBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        df = block_input.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        df["sma_short_diff"] = (df["sma_short"] - df["close"]) / df["sma_short"]
        df["sma_medium_diff"] = (df["sma_medium"] - df["close"]) / df["sma_medium"]
        df["sma_long_diff"] = (df["sma_long"] - df["close"]) / df["sma_long"]
        # difference from sma_long
        df["sma_long_short"] = (df["sma_long"] - df["sma_short"]) / df["sma_long"]
        df["sma_long_medium"] = (df["sma_long"] - df["sma_medium"]) / df["sma_long"]
        params = {
            "sma_short_diff": df["sma_short_diff"].tail(3).mean(),
            "sma_medium_diff": df["sma_medium_diff"].tail(3).mean(),
            "sma_long_diff": df["sma_long_diff"].tail(3).mean(),
            "sma_long_short": df["sma_long_short"].tail(3).mean(),
            "sma_long_medium": df["sma_long_medium"].tail(3).mean(),
            "sma_impact": self._get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return ParameterizeSmaBlockOutput.of(series=None, params=params)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=ParameterizeSmaBlockInput)
