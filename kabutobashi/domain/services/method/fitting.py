from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from .method import Method, MethodType


@dataclass(frozen=True)
class Fitting(Method):
    """
    1次、2次、3次の関数でfittingした値を返す
    """

    method_name: str = "fitting"
    method_type: MethodType = MethodType.TECHNICAL_ANALYSIS

    @staticmethod
    def _linear_fit(x, a, b):
        return a * x + b

    @staticmethod
    def _square_fit(x, a, b, c):
        return a * x * x + b * x + c

    @staticmethod
    def _cube_fit(x, a, b, c, d):
        return a * x * x * x + b * x * x + c * x + d

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        array_y = df["close"]
        array_x = np.array(range(0, len(array_y)))

        linear_param, _ = curve_fit(self._linear_fit, array_x, array_y)
        square_param, _ = curve_fit(self._square_fit, array_x, array_y)
        cube_param, _ = curve_fit(self._cube_fit, array_x, array_y)
        df_ = df.copy()
        df_["linear_fitting"] = [self._linear_fit(x, *linear_param) for x in array_x]
        df_["square_fitting"] = [self._square_fit(x, *square_param) for x in array_x]
        df_["cube_fitting"] = [self._cube_fit(x, *cube_param) for x in array_x]
        return df_

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df_ = df.copy()
        df_["diff"] = -1
        # 正負が交差した点
        df_ = df_.join(self._cross(df_["diff"]))
        df_ = df_.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df_

    def _color_mapping(self) -> list:
        return [
            {"df_key": "linear_fitting", "color": "#dc143c", "label": "linear"},
            {"df_key": "square_fitting", "color": "#ffa500", "label": "square"},
            {"df_key": "cube_fitting", "color": "#1e90ff", "label": "cube"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "in"}

    def _processed_columns(self) -> list:
        return ["linear_fitting", "square_fitting", "cube_fitting"]

    def _parameterize(self, df_x: pd.DataFrame, df_p: pd.DataFrame) -> dict:
        array_y = df_x["close"]
        array_x = np.array(range(0, len(array_y)))

        linear_param, _ = curve_fit(self._linear_fit, array_x, array_y)
        square_param, _ = curve_fit(self._square_fit, array_x, array_y)
        cube_param, _ = curve_fit(self._cube_fit, array_x, array_y)

        return {
            "linear_x_1": linear_param[0],
            "linear_x_0": linear_param[1],
            "square_x_2": square_param[0],
            "square_x_1": square_param[1],
            "square_x_0": square_param[2],
            "cube_x_3": cube_param[0],
            "cube_x_2": cube_param[1],
            "cube_x_1": cube_param[2],
            "cube_x_0": cube_param[3],
        }
