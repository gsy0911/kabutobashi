from datetime import datetime, timedelta

import jpholiday
import numpy as np
import pandas as pd

from kabutobashi.domain.method import *

from .errors import KabutobashiBaseError, StockDfError


def get_past_n_days(current_date: str, n: int = 60) -> list:
    """
    土日と祝日を考慮したn営業日前までの日付のリストを返す関数

    Args:
        current_date: n日前を計算する起点となる日
        n: n日前

    Returns:
        date list, ex ["%Y-%m-%d", "%Y-%m-%d", "%Y-%m-%d", ...]
    """
    multiply_list = [2, 4, 8, 16]
    for multiply in multiply_list:
        return_candidate = _get_past_n_days(current_date=current_date, n=n, multiply=multiply)
        if len(return_candidate) == n:
            return return_candidate
    raise KabutobashiBaseError(f"{n}日前を正しく取得できませんでした")


def _get_past_n_days(current_date: str, n: int, multiply: int) -> list:
    """
    n*multiplyの日数分のうち、商取引が行われる日を取得する

    Args:
        current_date: n日前を計算する起点となる日
        n: n日前
        multiply: n日前にかける数。
    """
    end_date = datetime.strptime(current_date, "%Y-%m-%d")
    # 2倍しているのは土日や祝日が排除されるため
    # また、nが小さすぎると休日が重なった場合に日数の取得ができないため
    back_n_days = n * multiply
    date_candidate = [end_date - timedelta(days=d) for d in range(back_n_days)]
    # 土日を除く
    filter_weekend = [d for d in date_candidate if d.weekday() < 5]
    # 祝日を除く
    filter_holiday = [d for d in filter_weekend if not jpholiday.is_holiday(d)]
    # 文字列に日付を変えてreturn
    return list(map(lambda x: x.strftime("%Y-%m-%d"), filter_holiday[:n]))


def compute_fitting(array_y: list, prefix: str) -> dict:
    from scipy.optimize import curve_fit

    statistical_values = {}
    array_x = np.array(range(0, len(array_y)))

    def _linear_fit(x, a, b):
        return a * x + b

    def _square_fit(x, a, b, c):
        return a * x * x + b * x + c

    def _cube_fit(x, a, b, c, d):
        return a * x * x * x + b * x * x + c * x + d

    linear_param, _ = curve_fit(_linear_fit, array_x, array_y)
    statistical_values.update({f"{prefix}_linear_{idx}": p for idx, p in enumerate(linear_param[:-1])})
    square_param, _ = curve_fit(_square_fit, array_x, array_y)
    statistical_values.update({f"{prefix}_square_{idx}": p for idx, p in enumerate(square_param[:-1])})
    cube_param, _ = curve_fit(_cube_fit, array_x, array_y)
    statistical_values.update({f"{prefix}_cube_{idx}": p for idx, p in enumerate(cube_param[:-1])})
    return statistical_values


def compute_statistical_values(stock_df: pd.DataFrame, fitting_term: int = 10, taken: int = 5) -> dict:
    # create and initialize instance
    _sma = SMA(short_term=5, medium_term=21, long_term=70)
    _macd = MACD(short_term=12, long_term=26, macd_span=9)
    _adx = ADX()
    _stochastics = Stochastics()

    statistical_values = {}
    statistical_values.update(compute_fitting(stock_df["close"], prefix="close"))
    # params with SMA0
    sma_df = stock_df.pipe(_sma)
    statistical_values.update(compute_fitting(sma_df["sma_short"][-fitting_term:], "sma_short"))
    statistical_values.update(compute_fitting(sma_df["sma_medium"][-fitting_term:], "sma_medium"))
    statistical_values.update(compute_fitting(sma_df["sma_long"][-fitting_term:], "sma_long"))
    # params with MACD
    macd_df = stock_df.pipe(_macd)
    statistical_values.update({f"histogram_{idx}": v for idx, v in enumerate(macd_df[-taken:]["histogram"].values)})
    adx_df = stock_df.pipe(_adx)
    statistical_values.update({f"plus_di_{idx}": v for idx, v in enumerate(adx_df[-taken:]["plus_di"].values)})
    statistical_values.update({f"minus_di_{idx}": v for idx, v in enumerate(adx_df[-taken:]["minus_di"].values)})
    statistical_values.update({f"ADX_{idx}": v for idx, v in enumerate(adx_df[-taken:]["ADX"].values)})
    statistical_values.update({f"ADXR_{idx}": v for idx, v in enumerate(adx_df[-taken:]["ADXR"].values)})
    # params with Stochastics
    stochastics_df = stock_df.pipe(_stochastics)
    statistical_values.update({f"D_{idx}": v for idx, v in enumerate(stochastics_df[-taken:]["D"].values)})
    statistical_values.update({f"SD_{idx}": v for idx, v in enumerate(stochastics_df[-taken:]["SD"].values)})

    return statistical_values
