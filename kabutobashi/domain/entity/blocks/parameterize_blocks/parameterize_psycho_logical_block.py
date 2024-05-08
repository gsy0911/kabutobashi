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


@inject
@dataclass(frozen=True)
class ParameterizePsychoLogicalBlock(IParameterizeBlock):

    def _process(self) -> ParameterizePsychoLogicalBlockOutput:
        if not isinstance(self.block_input, ParameterizePsychoLogicalBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        df = self.block_input.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "psycho_line": df["psycho_line"].tail(3).mean(),
            "psycho_logical_impact": self._get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return ParameterizePsychoLogicalBlockOutput.of(series=None, params=params)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=ParameterizePsychoLogicalBlockInput)
