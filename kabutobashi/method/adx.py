import pandas as pd
from .method import Method
from kabutobashi.attributes import Field
import matplotlib.pyplot as plt


class ADX(Method):
    """
    相場のトレンドの強さを見るための指標である`ADX`を計算するクラス。

    以下の指標を計算するクラス

    * +DI: 株価の上昇の大きさ
    * -DI: 株価の下降の大きさ
    * ADX: 株価のトレンドの強さ
    * ADXR: ADXの単純移動平均線

    Args:
        term (int):
        adx_term (int):
        adxr_term (int):

    See Also:
        * https://www.sevendata.co.jp/shihyou/technical/dmi.html
        * https://www.sevendata.co.jp/shihyou/technical/adx.html

    """

    term = Field(required_type=int)
    adx_term = Field(required_type=int)
    adxr_term = Field(required_type=int)

    def __init__(self, term=14, adx_term=14, adxr_term=28):
        super().__init__(method_name="adx")
        self.term = term
        self.adx_term = adx_term
        self.adxr_term = adxr_term

    @staticmethod
    def _true_range(x: pd.DataFrame):
        """

        Args:
            x (pd.DataFrame)

        Returns:
            maximum
        """
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
    def _compute_dx(x: pd.DataFrame) -> float:
        """

        Args:
            x (pd.DataFrame):
        """
        numerator = abs(x['plus_di'] - x['minus_di'])
        denominator = x['plus_di'] + x['minus_di']
        return numerator / denominator * 100

    @staticmethod
    def _fixed_plus_dm(x: pd.DataFrame) -> float:
        if x['plus_dm'] > 0 and x['plus_dm'] > x['minus_dm']:
            return x['plus_dm']
        else:
            return 0

    @staticmethod
    def _fixed_minus_dm(x: pd.DataFrame) -> float:
        if x['minus_dm'] > 0 and x['minus_dm'] > x['plus_dm']:
            return x['minus_dm']
        else:
            return 0

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
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
            fixed_plus_dm=_df.apply(lambda x: self._fixed_plus_dm(x), axis=1),
            fixed_minus_dm=_df.apply(lambda x: self._fixed_minus_dm(x), axis=1)
        )
        _df = _df.assign(
            true_range=_df.apply(lambda x: self._true_range(x), axis=1),
            sum_tr=lambda x: x['true_range'].rolling(self.term).sum(),
            sum_plus_dm=lambda x: x['fixed_plus_dm'].rolling(self.term).sum(),
            sum_minus_dm=lambda x: x['fixed_minus_dm'].rolling(self.term).sum()
        )

        _df = _df.dropna()
        required_columns = ["open", "high", "low", "close", "sum_plus_dm", "sum_minus_dm", "sum_tr"]
        _df = _df.loc[:, required_columns]
        
        # +DI, -DI
        _df = _df.assign(
            plus_di=_df.apply(lambda x: x['sum_plus_dm'] / x['sum_tr'] * 100, axis=1),
            minus_di=_df.apply(lambda x: x['sum_minus_dm'] / x['sum_tr'] * 100, axis=1)
        )
        _df = _df.assign(
            DX=_df.apply(self._compute_dx, axis=1),
            ADX=lambda x: x['DX'].rolling(self.adx_term).mean(),
            ADXR=lambda x: x['DX'].rolling(self.adxr_term).mean()
        )
        return _df

    @staticmethod
    def _buy_signal(x) -> float:
        """
        DMIとADXを組み合わせた基本パターン
        """
        
        # +DIが-DIを上抜き、ADXが上昇傾向の上向きであれば新規買い
        if x['ADX_trend'] > 0:
            if x['to_plus'] > 0:
                return 1
        
        # +DIが-DIより上に位置している際に、
        # ADXが下向きから上向きに転換した場合
        # if x['diff'] > 0:

    @staticmethod
    def _sell_signal(x) -> float:
        """
        DMIとADXを組み合わせた基本パターン        
        """
        # -DIが+DIを下抜き、ADXが下落傾向の下向きであれば新規空売り
        if x['ADX_trend'] < 0:
            if x['to_minus'] > 0:
                return 1
        
    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        """
        buy_signalとsell_signalを付与
        """
        _df['ADX_trend'] = self._trend(_df['ADX'])
        _df['diff'] = _df['plus_di'] - _df['minus_di']
        _df = _df.join(self._cross(_df['diff']))
        
        _df['buy_signal'] = _df.apply(lambda x: self._buy_signal)
        _df['sell_signal'] = _df.apply(lambda x: self._sell_signal)

        return _df

    def _visualize(self, _df: pd.DataFrame):
        fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(6, 5))
        # x軸のオートフォーマット
        fig.autofmt_xdate()

        # set candlestick
        self.add_ax_candlestick(ax1, _df)

        # plot adx
        ax2.plot(_df.index, _df['plus_di'], label="+DI")
        ax2.plot(_df.index, _df['minus_di'], label="-di")
        ax2.plot(_df.index, _df['ADX'], label="ADX")
        ax2.plot(_df.index, _df['ADXR'], label="ADXR")
        ax2.legend(loc="center left")  # 各線のラベルを表示

        ax1.legend(loc="best")  # 各線のラベルを表示
        return fig
