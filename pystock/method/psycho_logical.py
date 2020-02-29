import pandas as pd
from pystock.method.method import Method
import matplotlib.pyplot as plt
from pystock.attributes.attribute import Field


class PsychoLogical(Method):
    """
    https://www.sevendata.co.jp/shihyou/technical/psycho.html
    """
    upper_threshold = Field(required_type=float)
    lower_threshold = Field(required_type=float)
    psycho_term = Field(required_type=int)

    def __init__(self, upper_threshold=0.75, lower_threshold=0.25, psycho_term=12):
        super().__init__()
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.psycho_term = psycho_term

    def method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df['shift_close'] = _df['close'].shift(1)
        # _df = _df.assign(
        #    diff=_df.apply(lambda x: x['close'] - x['shift_close'], axis=1),
        #    is_raise=lambda x: 1 if x['diff'] > 0 else 0,
        #    psycho_sum=lambda x: x['is_raise'].rolling(self.psycho_term).sum(),
        #    bought_too_much=lambda x: 1 if x['psycho_line'] > self.uuper_threshold else 0,
        #    sold_too_much=lambda x: 1 if x['psycho_line'] < self.lower_threshold else 0
        # )
        _df['diff'] = _df.apply(lambda x: x['close']-x['shift_close'], axis=1)
        
        _df['is_raise'] = _df['diff'].apply(lambda x: 1 if x > 0 else 0)
        
        _df['psycho_sum'] = _df['is_raise'].rolling(self.psycho_term).sum()
        _df['psycho_line'] = _df['psycho_sum'].apply(lambda x: x/self.psycho_term)
        
        _df['bought_too_much'] = _df['psycho_line'].apply(lambda x: 1 if x > self.upper_threshold else 0)
        _df['sold_too_much'] = _df['psycho_line'].apply(lambda x: 1 if x < self.lower_threshold else 0)
        return _df

    def signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        return _df

    def visualize(self, _df: pd.DataFrame):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 5))
        # x軸のオートフォーマット
        fig.autofmt_xdate()

        # set candlestick
        self.add_ax_candlestick(ax, _df)

        # plot macd
        ax.legend(loc="best")  # 各線のラベルを表示
        return fig
