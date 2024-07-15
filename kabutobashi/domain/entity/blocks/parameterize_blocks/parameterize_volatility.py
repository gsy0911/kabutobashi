import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block
from .abc_parameterize_block import get_impact


@block(
    block_name="parameterize_volatility",
    series_required_columns=["high", "low", "close"],
)
class ParameterizeVolatilityBlock:
    """
    変動幅を計算する
    """

    series: pd.DataFrame

    def _process(self) -> dict:
        df = self.series
        df["volatility"] = (df["high"] - df["low"]) / df["close"]
        volatility_ = df["volatility"].mean()
        close_volatility = max(df["close"]) - min(df["close"]) / df["close"].median()
        return {
            "volatility": volatility_,
            "close_volatility": close_volatility,
            "dt": max(df.index.to_list()),
        }
