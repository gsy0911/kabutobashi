import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block
from .abc_parameterize_block import get_impact


@block(
    block_name="parameterize_adx", series_required_columns=["DX", "ADX", "ADXR", "adx_buy_signal", "adx_sell_signal"]
)
class ParameterizeAdxBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "adx_dx": df["DX"].tail(3).mean(),
            "adx_adx": df["ADX"].tail(3).mean(),
            "adx_adxr": df["ADXR"].tail(3).mean(),
            "adx_impact": get_impact(df=df, influence=self.influence, tail=self.tail, prefix="adx"),
            "dt": max(df.index.to_list()),
        }
        return params
