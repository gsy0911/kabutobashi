import pandas as pd
from kabutobashi.method.method import Method
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt


class Fitting(Method):
    """

    """

    def __init__(self):
        super().__init__(method_name="macd")

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        """
        macdを基準として今後上昇するかどうかをスコアで返す。
        値が大きければその傾向が高いことを表している。
        最小値は0で、最大値は無限大である。
        :param _df:
        :return:
        """
        # histogramが図として表現されるMACDの値
        array_y = _df['close']
        array_x = np.array(range(0, len(array_y)))

        def _linear_fit(x, a, b):
            return a*x + b

        def _square_fit(x, a, b, c):
            return a*x*x + b*x + c

        def _cube_fit(x, a, b, c, d):
            return a*x*x*x + b*x*x + c*x + d

        linear_param, _ = curve_fit(_linear_fit, array_x, array_y)
        square_param, _ = curve_fit(_square_fit, array_x, array_y)
        cube_param, _ = curve_fit(_cube_fit, array_x, array_y)
        _df['linear_fitting'] = [_linear_fit(x, *linear_param) for x in array_x]
        _df['square_fitting'] = [_square_fit(x, *square_param) for x in array_x]
        _df['cube_fitting'] = [_cube_fit(x, *cube_param) for x in array_x]
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        return _df

    def _visualize(self, _df: pd.DataFrame):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 5))
        # x軸のオートフォーマット
        fig.autofmt_xdate()

        # set candlestick
        self.add_ax_candlestick(ax, _df)

        # plot
        ax.plot(_df.index, _df['linear_fitting'], color="#dc143c", label="linear")
        ax.plot(_df.index, _df['square_fitting'], color="#ffa500", label="square")
        ax.plot(_df.index, _df['cube_fitting'], color="#1e90ff", label="cube")

        ax.legend(loc="best")  # 各線のラベルを表示
        return fig
