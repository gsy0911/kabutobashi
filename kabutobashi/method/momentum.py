import pandas as pd
from kabutobashi.method.method import Method
from kabutobashi.attributes import Field


class Momentum(Method):
    """
    See Also:
        https://www.sevendata.co.jp/shihyou/technical/momentum.html
    """
    term = Field()

    def __init__(self, term=25):
        super().__init__(method_name="momentum")
        self.term = term

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            momentum=_df['close'].shift(10),
            sma_momentum=lambda x: x['momentum'].rolling(self.term).mean()
        )
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.join(self._cross(_df['sma_momentum']))
        _df = _df.rename(columns={
            "to_plus": "buy_signal",
            "to_minus": "sell_signal"
        })
        return _df
