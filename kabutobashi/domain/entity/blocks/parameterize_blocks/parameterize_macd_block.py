import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block
from .abc_parameterize_block import get_impact


@block(
    block_name="parameterize_macd",
    series_required_columns=["signal", "histogram", "macd_buy_signal", "macd_sell_signal"],
)
class ParameterizeMacdBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "signal": df["signal"].tail(3).mean(),
            "histogram": df["histogram"].tail(3).mean(),
            "macd_impact": get_impact(df=df, influence=self.influence, tail=self.tail, prefix="macd"),
        }

        return params
