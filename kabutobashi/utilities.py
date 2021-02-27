from datetime import datetime, timedelta
import jpholiday
import numpy as np
import pandas as pd
from .errors import PyStockBaseError, StockDfError


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
    raise PyStockBaseError(f"{n}日前を正しく取得できませんでした")


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


def iter_by_code(stock_df: pd.DataFrame, days_thresholds: int = 60) -> (int, pd.DataFrame):
    """
    銘柄コードでイテレーションを回しつつ、必要なデータ数がある銘柄のDataFrameのみを返す関数。

    Args:
        stock_df:
        days_thresholds:

    Returns:
        (code: int, _df: pd.DataFrame)
    """
    for code, _df in stock_df.groupby("code"):
        if len(_df.index) < days_thresholds:
            continue
        else:
            yield code, format_to_stock_df(_df)


def replace_comma(x) -> float:
    """
    pandas内の値がカンマ付きの場合に、カンマを削除する関数

    Args:
        x:

    Returns:

    """
    if type(x) is str:
        x = x.replace(",", "")
    try:
        f = float(x)
    except ValueError:
        raise StockDfError(f"floatに変換できる値ではありません。")
    return f


def format_to_stock_df(_df: pd.DataFrame) -> pd.DataFrame:
    stock_df = _df \
        .replace("---", np.nan) \
        .dropna(subset=["open", "close", "high", "low"]) \
        .fillna(0) \
        .assign(
            open=_df['open'].apply(replace_comma),
            close=_df['close'].apply(replace_comma),
            high=_df['high'].apply(replace_comma),
            low=_df['low'].apply(replace_comma),
            volume=_df['volume'].apply(replace_comma),
        ) \
        .convert_dtypes()
    return stock_df


def train_test_sliding_split(
        stock_df: pd.DataFrame,
        *,
        buy_sell_term_days: int = 5,
        sliding_window: int = 60,
        step: int = 2):
    """

    Args:
        stock_df:
        buy_sell_term_days:
        sliding_window:
        step:

    Returns:

    """
    df_length = len(stock_df.index)
    if df_length < buy_sell_term_days + sliding_window:
        raise StockDfError("入力されたDataFrameの長さがwindow幅よりも小さいです")
    loop = df_length - (buy_sell_term_days + sliding_window)
    for idx, i in enumerate(range(0, loop, step)):
        offset = i+sliding_window
        yield idx, stock_df[i: offset], stock_df[offset: offset + buy_sell_term_days]
