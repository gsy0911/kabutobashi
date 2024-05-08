from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockSeriesIsNoneError

from ..abc_block import BlockGlue, IBlockInput, IBlockOutput
from .abc_parameterize_block import IParameterizeBlock


@dataclass(frozen=True)
class ParameterizeAdxBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        processed_adx_series = block_glue.block_outputs["process_adx"].series
        if processed_adx_series is None:
            raise KabutobashiBlockSeriesIsNoneError()

        return ParameterizeAdxBlockInput(series=processed_adx_series, params={})

    def _validate(self):
        if self.series is not None:
            columns = self.series.columns
            assert "DX" in columns, "ParameterizeAdxBlockInput must have 'DX' column"
            assert "ADX" in columns, "ParameterizeAdxBlockInput must have 'ADX' column"
            assert "ADXR" in columns, "ParameterizeAdxBlockInput must have 'ADXR' column"


@dataclass(frozen=True)
class ParameterizeAdxBlockOutput(IBlockOutput):
    block_name: str = "parameterize_adx"

    def _validate(self):
        keys = self.params.keys()
        assert "adx_dx" in keys, "ParameterizeAdxBlockOutput must have 'adx_dx' column"
        assert "adx_adx" in keys, "ParameterizeAdxBlockOutput must have 'adx_adx' column"
        assert "adx_adxr" in keys, "ParameterizeAdxBlockOutput must have 'adx_adxr' column"
        assert "adx_impact" in keys, "ParameterizeAdxBlockOutput must have 'adx_impact' column"


@inject
@dataclass(frozen=True)
class ParameterizeAdxBlock(IParameterizeBlock):

    def _process(self) -> ParameterizeAdxBlockOutput:
        if not isinstance(self.block_input, ParameterizeAdxBlockInput):
            raise KabutobashiBlockInstanceMismatchError()

        df = self.block_input.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "adx_dx": df["DX"].tail(3).mean(),
            "adx_adx": df["ADX"].tail(3).mean(),
            "adx_adxr": df["ADXR"].tail(3).mean(),
            "adx_impact": self._get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return ParameterizeAdxBlockOutput.of(series=None, params=params)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=ParameterizeAdxBlockInput)
