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
class ParameterizeStochasticsBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        initial_series = block_glue.series
        if initial_series is None:
            raise KabutobashiBlockSeriesIsNoneError()
        processed_stochastics_series = block_glue.block_outputs["process_stochastics"].series
        if processed_stochastics_series is None:
            raise KabutobashiBlockSeriesIsNoneError()

        return ParameterizeStochasticsBlockInput(
            series=processed_stochastics_series.join(initial_series["close"]), params={}
        )

    def _validate(self):
        if self.series is not None:
            columns = self.series.columns
            assert "K" in columns, "ParameterizeStochasticsBlockInput must have 'K' column"
            assert "D" in columns, "ParameterizeStochasticsBlockInput must have 'D' column"
            assert "SD" in columns, "ParameterizeStochasticsBlockInput must have 'SD' column"
            assert "buy_signal" in columns, "ParameterizeStochasticsBlockInput must have 'buy_signal' column"
            assert "sell_signal" in columns, "ParameterizeStochasticsBlockInput must have 'sell_signal' column"


@dataclass(frozen=True)
class ParameterizeStochasticsBlockOutput(IBlockOutput):
    block_name: str = "parameterize_stochastics"

    def _validate(self):
        keys = self.params.keys()
        assert "stochastics_k" in keys, "ParameterizeStochasticsBlockOutput must have 'stochastics_k' column"
        assert "stochastics_d" in keys, "ParameterizeStochasticsBlockOutput must have 'stochastics_d' column"
        assert "stochastics_sd" in keys, "ParameterizeStochasticsBlockOutput must have 'stochastics_sd' column"
        assert "stochastics_impact" in keys, "ParameterizeStochasticsBlockOutput must have 'stochastics_impact' column"


@inject
@dataclass(frozen=True)
class ParameterizeStochasticsBlock(IParameterizeBlock):

    def _process(self) -> ParameterizeStochasticsBlockOutput:
        if not isinstance(self.block_input, ParameterizeStochasticsBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        df = self.block_input.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "stochastics_k": df["K"].tail(3).mean(),
            "stochastics_d": df["D"].tail(3).mean(),
            "stochastics_sd": df["SD"].tail(3).mean(),
            "stochastics_impact": self._get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return ParameterizeStochasticsBlockOutput.of(series=None, params=params)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=ParameterizeStochasticsBlockInput)
