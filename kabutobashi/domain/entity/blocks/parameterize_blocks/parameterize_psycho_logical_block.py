import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block
from .abc_parameterize_block import get_impact


@block(
    block_name="parameterize_psycho_logical",
    series_required_columns=["psycho_line", "psycho_logical_buy_signal", "psycho_logical_sell_signal"],
)
class ParameterizePsychoLogicalBlock:
    series: pd.DataFrame
    influence: int = 2
    tail: int = 5

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        params = {
            "psycho_line": df["psycho_line"].tail(3).mean(),
            "psycho_logical_impact": get_impact(
                df=df, influence=self.influence, tail=self.tail, prefix="psycho_logical"
            ),
            "dt": max(df.index.to_list()),
        }

        return params
