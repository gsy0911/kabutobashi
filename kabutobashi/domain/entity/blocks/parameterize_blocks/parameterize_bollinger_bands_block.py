import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block
from .abc_parameterize_block import get_impact


@block(
    block_name="parameterize_bollinger_bands",
    series_required_columns=["upper_1_sigma", "lower_1_sigma", "upper_2_sigma", "lower_2_sigma"],
)
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
