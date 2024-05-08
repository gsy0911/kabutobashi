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


@inject
@dataclass(frozen=True)
class ParameterizeMacdBlock(IParameterizeBlock):

    def _process(self) -> ParameterizeMacdBlockOutput:
        if not isinstance(self.block_input, ParameterizeMacdBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        df = self.block_input.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "signal": df["signal"].tail(3).mean(),
            "histogram": df["histogram"].tail(3).mean(),
            "macd_impact": self._get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return ParameterizeMacdBlockOutput.of(series=None, params=params)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=ParameterizeMacdBlockInput)
