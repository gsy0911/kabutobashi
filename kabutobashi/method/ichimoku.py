import pandas as pd
from kabutobashi.method.method import Method
from kabutobashi.attributes import Field
import matplotlib.pyplot as plt


class Ichimoku(Method):
    """

    See Also:
        https://kabu.com/investment/guide/technical/04.html
    """

    short_term = Field()
    medium_term = Field()
    long_term = Field

    def __init__(self, short_term=12, medium_term=26, long_term=52):
        super().__init__(method_name="ichimoku")
        self.short_term = short_term
        self.medium_term = medium_term
        self.long_term = long_term

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            # 短期の線
            short_max=lambda x: x['close'].rolling(self.short_term).max(),
            short_min=lambda x: x['close'].rolling(self.short_term).min(),
            # 中期の線
            medium_max=lambda x: x['close'].rolling(self.medium_term).max(),
            medium_min=lambda x: x['close'].rolling(self.medium_term).min(),
            # 長期線
            long_max=lambda x: x['close'].rolling(self.long_term).max(),
            long_min=lambda x: x['close'].rolling(self.long_term).min()
        )

        # 指標の計算
        _df = _df.assign(
            line_change=lambda x: (x['short_max'] + x['short_min']) / 2,
            line_base=lambda x: (x['medium_max'] + x['medium_min']) / 2,
            # 先行線
            proceding_span_1=lambda x: (x['line_change'] + x['line_base']) / 2,
            proceding_span_2=lambda x: (x['long_max'] + x['long_min']) / 2
        )

        # 値のshift
        _df = _df.assign(
            proceding_span_1=_df['proceding_span_1'].shift(26),
            proceding_span_2=_df['proceding_span_2'].shift(26),
            delayed_span=_df['close'].shift(26)
        )
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        return _df

    def _visualize(self, _df: pd.DataFrame):
        # TODO implement
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 5))
        # x軸のオートフォーマット
        fig.autofmt_xdate()

        # set candlestick
        self.add_ax_candlestick(ax, _df)

        # plot macd
        ax.plot(_df.index, _df['sma_long'], color="#dc143c", label="sma_long")

        ax.legend(loc="best")  # 各線のラベルを表示
        return fig
