import pandas as pd
from pystock.method.method import Method
# import matplotlib.pyplot as plt
from pystock.attributes.attribute import Field


class Momentum(Method):
    """
    https://www.sevendata.co.jp/shihyou/technical/momentum.html
    """
    term = Field()

    def __init__(self, term=25):
        super().__init__()
        self.term = term

    def method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            momentum=_df['close'].shift(10),
            sma_momentum=lambda x: x['momentum'].rolling(self.term).mean()
        )
        return _df

    def signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.join(self.cross(_df['sma_momentum']))
        _df = _df.rename(columns={
            "to_plus": "buy_signal",
            "to_minus": "sell_signal"
        })
        return _df

    # def visualize(self, _df: pd.DataFrame):
    #     fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 5))
    #     # x軸のオートフォーマット
    #     fig.autofmt_xdate()
    #
    #     # set candlestick
    #     self.add_ax_candlestick(ax, _df)
    #
    #     # plot macd
    #     ax.legend(loc="best")  # 各線のラベルを表示
    #     return fig
