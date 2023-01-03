from datetime import datetime, timedelta
from typing import Union

import jpholiday

from kabutobashi.domain.errors import KabutobashiBaseError, KabutobashiEntityError


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


def replace(input_value: str) -> str:
    if input_value == "-":
        return "0"
    elif input_value == "":
        return "0"
    return input_value.replace("---", "0").replace("円", "").replace("株", "").replace("倍", "").replace(",", "")


def convert_float(input_value: Union[str, float, int]) -> float:
    if type(input_value) is float:
        return input_value
    elif type(input_value) is int:
        return float(input_value)
    elif type(input_value) is str:
        try:
            return float(replace(input_value=input_value))
        except ValueError as e:
            raise KabutobashiEntityError(f"cannot convert {input_value} to float: {e}")
    raise KabutobashiEntityError(f"cannot convert {input_value} to float")


def convert_int(input_value: Union[str, float, int]) -> int:
    if type(input_value) == int:
        return input_value
    elif type(input_value) == float:
        try:
            return int(input_value)
        except ValueError:
            return 0
    elif type(input_value) is str:
        try:
            return int(replace(input_value=input_value))
        except ValueError as e:
            raise KabutobashiEntityError(f"cannot convert {input_value} to integer: {e}")
    else:
        try:
            return int(input_value)
        except Exception:
            raise KabutobashiEntityError(f"cannot convert {input_value} to int")
