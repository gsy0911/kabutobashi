import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block
from .abc_parameterize_block import get_impact


@block(
    block_name="parameterize_sma",
    series_required_columns=["sma_short", "sma_medium", "sma_long", "close", "sma_buy_signal", "sma_sell_signal"],
)
class ParameterizeSmaBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
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
            "sma_impact": get_impact(df=df, influence=self.influence, tail=self.tail, prefix="sma"),
            "dt": max(df.index.to_list()),
        }

        return params
