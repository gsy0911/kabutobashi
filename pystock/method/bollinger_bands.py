import pandas as pd
from pystock.method.method import Method
# import matplotlib.pyplot as plt
from pystock.attributes.attribute import Field


class BollingerBands(Method):
    band_term = Field()
    continuity_term = Field()

    def __init__(self, band_term=12, continuity_term=10):
        super().__init__()
        self.band_term = band_term
        self.continuity_term = continuity_term

    def method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            mean=_df['close'].rolling(self.band_term).mean(),
            std=_df['close'].rolling(self.band_term).std()
        )
        _df = _df.assign(
            upper_2_sigma=_df.apply(lambda x: x['mean'] + x['std'] * 2, axis=1),
            lower_2_sigma=_df.apply(lambda x: x['mean'] - x['std'] * 2, axis=1)
        )
        return _df

    def signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            over_upper=_df.apply(lambda x: 1 if x['close'] > x['upper_2_sigma'] else 0, axis=1),
            over_lower=_df.apply(lambda x: 1 if x['close'] < x['lower_2_sigma'] else 0, axis=1),
            over_upper_continuity=lambda x: x['over_upper'].rolling(self.continuity_term).sum(),
            over_lower_continuity=lambda x: x['over_lower'].rolling(self.continuity_term).sum()  
        )
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
