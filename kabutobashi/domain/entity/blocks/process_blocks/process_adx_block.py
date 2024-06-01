import pandas as pd

from ..decorator import block
from .abc_process_block import cross

__all__ = ["ProcessAdxBlock"]


@block(block_name="process_adx", series_required_columns=["high", "low", "close"])
class ProcessAdxBlock:
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

    series: pd.DataFrame
    term: int = 14
    adx_term: int = 14
    adxr_term: int = 28

    @staticmethod
    def _true_range(x: pd.DataFrame):
        """

        Args:
            x (pd.DataFrame)

        Returns:
            maximum
        """
        if x["high"] is pd.NA or x["low"] is pd.NA or x["shift_close"] is pd.NA:
            return 0
        current_high = x["high"]
        current_low = x["low"]
        prev_close = x["shift_close"]
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
        numerator = abs(x["plus_di"] - x["minus_di"])
        denominator = x["plus_di"] + x["minus_di"]
        try:
            return numerator / denominator * 100
        except ZeroDivisionError:
            return 0

    @staticmethod
    def _fixed_plus_dm(x: pd.DataFrame) -> float:
        if x["plus_dm"] is pd.NA or x["minus_dm"] is pd.NA:
            return 0
        if x["plus_dm"] > 0 and x["plus_dm"] > x["minus_dm"]:
            return x["plus_dm"]
        else:
            return 0

    @staticmethod
    def _fixed_minus_dm(x: pd.DataFrame) -> float:
        if x["plus_dm"] is pd.NA or x["minus_dm"] is pd.NA:
            return 0
        if x["minus_dm"] > 0 and x["minus_dm"] > x["plus_dm"]:
            return x["minus_dm"]
        else:
            return 0

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        # 利用する値をshift
        df = df.assign(shift_high=df["high"].shift(1), shift_low=df["low"].shift(1), shift_close=df["close"].shift(1))
        df = df.assign(
            plus_dm=df.apply(lambda x: x["high"] - x["shift_high"], axis=1),
            minus_dm=df.apply(lambda x: x["shift_low"] - x["low"], axis=1),
        )
        df = df.assign(
            fixed_plus_dm=df.apply(lambda x: self._fixed_plus_dm(x), axis=1),
            fixed_minus_dm=df.apply(lambda x: self._fixed_minus_dm(x), axis=1),
        )
        df = df.assign(
            true_range=df.apply(lambda x: self._true_range(x), axis=1),
            sum_tr=lambda x: x["true_range"].rolling(self.term).sum(),
            sum_plus_dm=lambda x: x["fixed_plus_dm"].rolling(self.term).sum(),
            sum_minus_dm=lambda x: x["fixed_minus_dm"].rolling(self.term).sum(),
        )

        df = df.dropna()
        # +DI, -DI
        df = df.assign(
            plus_di=df.apply(lambda x: x["sum_plus_dm"] / x["sum_tr"] * 100, axis=1),
            minus_di=df.apply(lambda x: x["sum_minus_dm"] / x["sum_tr"] * 100, axis=1),
        )
        df = df.assign(
            DX=df.apply(self._compute_dx, axis=1),
            ADX=lambda x: x["DX"].rolling(self.adx_term).mean(),
            ADXR=lambda x: x["DX"].rolling(self.adxr_term).mean(),
        )
        return df

    @staticmethod
    def _buy_signal(x) -> float:
        """
        DMIとADXを組み合わせた基本パターン
        """

        # +DIが-DIを上抜き、ADXが上昇傾向の上向きであれば新規買い
        if x["ADX_trend"] > 0:
            if x["to_plus"] > 0:
                return 1
        return 0

        # +DIが-DIより上に位置している際に、
        # ADXが下向きから上向きに転換した場合
        # if x['diff'] > 0:

    @staticmethod
    def _sell_signal(x) -> float:
        """
        DMIとADXを組み合わせた基本パターン
        """
        # -DIが+DIを下抜き、ADXが下落傾向の下向きであれば新規空売り
        if x["ADX_trend"] < 0:
            if x["to_minus"] > 0:
                return 1
        return 0

    @staticmethod
    def _trend(_s: pd.Series) -> pd.Series:
        """
        ある系列_sのトレンドを計算する。
        差分のrolling_sumを返す
        """
        # shorten variable name
        col = "original"
        shifted = "shifted"

        # shiftしたDataFrameの作成
        shift_s = _s.shift(1)
        df = pd.DataFrame({col: _s, shifted: shift_s})
        df["diff"] = df["original"] - df["shifted"]
        df["diff_rolling_sum"] = df["diff"].rolling(5).sum()
        return df["diff_rolling_sum"]

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        buy_signalとsell_signalを付与
        """
        df["ADX_trend"] = self._trend(df["ADX"])
        df["diff"] = df["plus_di"] - df["minus_di"]
        df = df.join(cross(df["diff"]))

        df["adx_buy_signal"] = df.apply(lambda x: self._buy_signal)
        df["adx_sell_signal"] = df.apply(lambda x: self._sell_signal)

        return df

    def _process(self) -> pd.DataFrame:
        applied_df = self._apply(df=self.series)
        signal_df = self._signal(df=applied_df)
        return signal_df[["plus_di", "minus_di", "DX", "ADX", "ADXR", "adx_buy_signal", "adx_sell_signal"]]
