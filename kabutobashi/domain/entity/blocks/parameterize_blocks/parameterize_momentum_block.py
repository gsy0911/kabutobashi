import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block
from .abc_parameterize_block import get_impact


@block(block_name="parameterize_momentum", series_required_columns=["momentum_buy_signal", "momentum_sell_signal"])
class ParameterizeMomentumBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "momentum_impact": get_impact(df=df, influence=self.influence, tail=self.tail, prefix="momentum"),
            "dt": max(df.index.to_list()),
        }

        return params
