from dataclasses import dataclass

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..abc_block import BlockGlue, IBlockInput, IBlockOutput
from ..decorator import block
from .abc_parameterize_block import get_impact


@dataclass(frozen=True)
class ParameterizeBollingerBandsBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        processed_bollinger_bands_series = block_glue.block_outputs["process_bollinger_bands"].series
        if processed_bollinger_bands_series is None:
            raise KabutobashiBlockSeriesIsNoneError()

        return ParameterizeBollingerBandsBlockInput(series=processed_bollinger_bands_series, params={})

    def _validate(self):
        if self.series is not None:
            columns = self.series.columns
            assert "upper_1_sigma" in columns, "ParameterizeBollingerBandsBlockInput must have 'upper_1_sigma' column"
            assert "lower_1_sigma" in columns, "ParameterizeBollingerBandsBlockInput must have 'lower_1_sigma' column"
            assert "upper_2_sigma" in columns, "ParameterizeBollingerBandsBlockInput must have 'upper_2_sigma' column"
            assert "lower_2_sigma" in columns, "ParameterizeBollingerBandsBlockInput must have 'lower_2_sigma' column"


@dataclass(frozen=True)
class ParameterizeBollingerBandsBlockOutput(IBlockOutput):
    block_name: str = "parameterize_bollinger_bands"

    def _validate(self):
        keys = self.params.keys()
        assert "upper_1_sigma" in keys, "ParameterizeBollingerBandsBlockOutput must have 'upper_1_sigma' column"
        assert "lower_1_sigma" in keys, "ParameterizeBollingerBandsBlockOutput must have 'lower_1_sigma' column"
        assert "upper_2_sigma" in keys, "ParameterizeBollingerBandsBlockOutput must have 'upper_2_sigma' column"
        assert "lower_2_sigma" in keys, "ParameterizeBollingerBandsBlockOutput must have 'lower_2_sigma' column"
        assert (
            "bollinger_bands_impact" in keys
        ), "ParameterizeBollingerBandsBlockOutput must have 'bollinger_bands_impact' column"


@block(block_name="parameterize_bollinger_bands", pre_condition_block_name="process_bollinger_bands")
class ParameterizeBollingerBandsBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "upper_1_sigma": df["upper_1_sigma"].tail(3).mean(),
            "lower_1_sigma": df["lower_1_sigma"].tail(3).mean(),
            "upper_2_sigma": df["upper_2_sigma"].tail(3).mean(),
            "lower_2_sigma": df["lower_2_sigma"].tail(3).mean(),
            "bollinger_bands_impact": get_impact(df=df, influence=self.influence, tail=self.tail),
        }

        return params
