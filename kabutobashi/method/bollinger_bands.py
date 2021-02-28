import pandas as pd
from kabutobashi.method.method import Method
from kabutobashi.attributes import Field
import matplotlib.pyplot as plt


class BollingerBands(Method):
    """
    株価の勢いの変化や反転の目安、方向を見る`BollingerBands`を計算するクラス。

    See Also:
        * https://www.sevendata.co.jp/shihyou/technical/bori.html
    """
    band_term = Field()
    continuity_term = Field()

    def __init__(self, band_term=12, continuity_term=10):
        super().__init__(method_name="bollinger_bands")
        self.band_term = band_term
        self.continuity_term = continuity_term

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            mean=_df['close'].rolling(self.band_term).mean(),
            std=_df['close'].rolling(self.band_term).std()
        )
        _df = _df.assign(
            upper_1_sigma=_df.apply(lambda x: x['mean'] + x['std'] * 1, axis=1),
            lower_1_sigma=_df.apply(lambda x: x['mean'] - x['std'] * 1, axis=1),
            upper_2_sigma=_df.apply(lambda x: x['mean'] + x['std'] * 2, axis=1),
            lower_2_sigma=_df.apply(lambda x: x['mean'] - x['std'] * 2, axis=1),
            upper_3_sigma=_df.apply(lambda x: x['mean'] + x['std'] * 3, axis=1),
            lower_3_sigma=_df.apply(lambda x: x['mean'] - x['std'] * 3, axis=1),
        )
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            over_upper=_df.apply(lambda x: 1 if x['close'] > x['upper_2_sigma'] else 0, axis=1),
            over_lower=_df.apply(lambda x: 1 if x['close'] < x['lower_2_sigma'] else 0, axis=1),
            over_upper_continuity=lambda x: x['over_upper'].rolling(self.continuity_term).sum(),
            over_lower_continuity=lambda x: x['over_lower'].rolling(self.continuity_term).sum()
        )
        
        _df['buy_signal'] = _df['over_upper'].apply(lambda x: 1 if x > 0 else 0)
        _df['sell_signal'] = _df['over_lower'].apply(lambda x: 1 if x > 0 else 0)
        return _df

    def _visualize(self, _df: pd.DataFrame):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 5))
        # x軸のオートフォーマット
        fig.autofmt_xdate()

        # set candlestick
        self.add_ax_candlestick(ax, _df)

        # plot
        ax.plot(_df.index, _df['upper_1_sigma'], color="#dc143c", label="+1s")
        ax.plot(_df.index, _df['lower_1_sigma'], color="#dc143c", label="-1s")
        ax.plot(_df.index, _df['upper_2_sigma'], color="#ffa500", label="+2s")
        ax.plot(_df.index, _df['lower_2_sigma'], color="#ffa500", label="-2s")
        ax.plot(_df.index, _df['upper_3_sigma'], color="#1e90ff", label="+3s")
        ax.plot(_df.index, _df['lower_3_sigma'], color="#1e90ff", label="-3s")

        ax.legend(loc="best")  # 各線のラベルを表示
        return fig
