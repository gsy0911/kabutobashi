import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block
from .abc_parameterize_block import get_impact


@block(
    block_name="parameterize_stochastics",
    series_required_columns=["K", "D", "SD", "stochastics_buy_signal", "stochastics_sell_signal"],
)
class ParameterizeStochasticsBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "stochastics_k": df["K"].tail(3).mean(),
            "stochastics_d": df["D"].tail(3).mean(),
            "stochastics_sd": df["SD"].tail(3).mean(),
            "stochastics_impact": get_impact(df=df, influence=self.influence, tail=self.tail, prefix="stochastics"),
        }

        return params
