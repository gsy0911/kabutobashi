import pandas as pd
from pystock.method.method import Method
# import matplotlib.pyplot as plt
from pystock.attributes.attribute import Field


class ADX(Method):
    """
    以下の指標を計算するクラス
    +DI: 株価の上昇の大きさ
    -DI: 株価の下降の大きさ
    ADX: 株価のトレンドの強さ
    ADXR: ADXの単純移動平均線

    https://www.sevendata.co.jp/shihyou/technical/dmi.html
    https://www.sevendata.co.jp/shihyou/technical/adx.html
    """

    term = Field(required_type=int)
    adx_term = Field(required_type=int)
    adxr_term = Field(required_type=int)

    def __init__(self, term=14, adx_term=14, adxr_term=28):
        super().__init__()
        self.term = term
        self.adx_term = adx_term
        self.adxr_term = adxr_term

    @staticmethod
    def true_range(x: pd.DataFrame):
        current_high = x['high']
        current_low = x['low']
        prev_close = x['shift_close']
        a = current_high - current_low
        b = current_high - prev_close
        c = prev_close - current_low
        max_ab = max(a, b)
        max_ac = max(a, c)
        return max(max_ab, max_ac)

    @staticmethod
    def compute_DX(x: pd.DataFrame) -> float:
        numerator = abs(x['plus_di'] - x['minus_di'])
        denominator = x['plus_di'] + x['minus_di']
        return numerator / denominator * 100

    @staticmethod
    def fixed_plus_dm(x: pd.DataFrame) -> float:
        if x['plus_dm'] > 0 and x['plus_dm'] > x['minus_dm']:
            return x['plus_dm']
        else:
            return 0

    @staticmethod
    def fixed_minus_dm(x: pd.DataFrame) -> float:
        if x['minus_dm'] > 0 and x['minus_dm'] > x['plus_dm']:
            return x['minus_dm']
        else:
            return 0

    def method(self, _df: pd.DataFrame) -> pd.DataFrame:
        # 利用する値をshift
        _df = _df.assign(
            shift_high=_df['high'].shift(1),
            shift_low=_df['low'].shift(1),
            shift_close=_df['close'].shift(1)
        )
        _df = _df.assign(
            plus_dm=_df.apply(lambda x: x['high'] - x['shift_high'], axis=1),
            minus_dm=_df.apply(lambda x: x['shift_low'] - x['low'], axis=1)
        )
        _df = _df.assign(
            fixed_plus_dm=_df.apply(lambda x: self.fixed_plus_dm(x), axis=1),
            fixed_minus_dm=_df.apply(lambda x: self.fixed_minus_dm(x), axis=1)
        )
        _df = _df.assign(
            true_range=_df.apply(lambda x: self.true_range(x), axis=1),
            sum_tr=lambda x: x['true_range'].rolling(self.term).sum(),
            sum_plus_dm=lambda x: x['fixed_plus_dm'].rolling(self.term).sum(),
            sum_minus_dm=lambda x: x['fixed_minus_dm'].rolling(self.term).sum()
        )

        _df = _df.dropna()
        required_columns = ["sum_plus_dm", "sum_minus_dm", "sum_tr"]
        _df = _df.loc[:, required_columns]
        _df = _df.assign(
            plus_di=_df.apply(lambda x: x['sum_plus_dm'] / x['sum_tr'] * 100, axis=1),
            minus_di=_df.apply(lambda x: x['sum_minus_dm'] / x['sum_tr'] * 100, axis=1)
        )
        _df = _df.assign(
            DX=_df.apply(self.compute_DX, axis=1),
            ADX=lambda x: x['DX'].rolling(self.adx_term).mean(),
            ADXR=lambda x: x['DX'].rolling(self.adxr_term).mean()
        )
        return _df

    def signal(self, analyzed_df: pd.DataFrame) -> pd.DataFrame:
        return analyzed_df

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
