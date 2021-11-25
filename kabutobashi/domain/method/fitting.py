from dataclasses import dataclass

import numpy as np
import pandas as pd

from .method import Method


@dataclass(frozen=True)
class Fitting(Method):
    """ """

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
        from scipy.optimize import curve_fit

        # histogramが図として表現されるMACDの値
        array_y = _df["close"]
        array_x = np.array(range(0, len(array_y)))

        def _linear_fit(x, a, b):
            return a * x + b

        def _square_fit(x, a, b, c):
            return a * x * x + b * x + c

        def _cube_fit(x, a, b, c, d):
            return a * x * x * x + b * x * x + c * x + d

        linear_param, _ = curve_fit(_linear_fit, array_x, array_y)
        square_param, _ = curve_fit(_square_fit, array_x, array_y)
        cube_param, _ = curve_fit(_cube_fit, array_x, array_y)
        _df["linear_fitting"] = [_linear_fit(x, *linear_param) for x in array_x]
        _df["square_fitting"] = [_square_fit(x, *square_param) for x in array_x]
        _df["cube_fitting"] = [_cube_fit(x, *cube_param) for x in array_x]
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        return _df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "linear_fitting", "color": "#dc143c", "label": "linear"},
            {"df_key": "square_fitting", "color": "#ffa500", "label": "square"},
            {"df_key": "cube_fitting", "color": "#1e90ff", "label": "cube"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "in"}
