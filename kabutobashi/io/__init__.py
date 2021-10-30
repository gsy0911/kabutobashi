"""
io module provides input/output method
"""

from datetime import datetime
from typing import Optional, Union

import pandas as pd
from kabutobashi.domain.entity import StockInfo


def example_data() -> pd.DataFrame:
    """
    get example stock data

    Returns:
        stock data
    """
    data_path_list = ["../data/stooq.csv"]
    _df = read_csv(data_path_list)
    _df = _df.sort_values("date", ascending=True)
    _df = _df.convert_dtypes()
    return _df


def read_csv(path_candidate: Union[str, list], **kwargs) -> Optional[pd.DataFrame]:
    """
    通常のread_csvの関数に加えて、strとlist[str]の場合に縦方向に結合してDataFrameを返す

    Args:
        path_candidate: "path" or ["path_1", "path_2"]

    Returns:
        株のDataFrame
    """
    if type(path_candidate) is str:
        return pd.read_csv(path_candidate, **kwargs)
    elif type(path_candidate) is list:
        if not path_candidate:
            return None
        df_list = [pd.read_csv(p, **kwargs) for p in path_candidate]
        return pd.concat(df_list)
    else:
        return None


def read_stock_csv(
    path_candidate: Union[str, list],
    code_list: Optional[list] = None,
    drop_reit: bool = True,
    row_more_than: Optional[int] = None,
    **kwargs
) -> Optional[pd.DataFrame]:
    """
    本APIにてCrawlしたデータを扱いやすい形式にデータ変換する関数

    Args:
        path_candidate: "path" or ["path_1", "path_2"]
        code_list: filter with code_list
        drop_reit: drop REIT-data if True
        row_more_than: filter specified code, which has {row_more_than} data

    Returns:
        株のDataFrame
    """
    df = read_csv(path_candidate, **kwargs)
    if df is None:
        return None
    else:
        decoded_df = _decode_stock_data(_df=df)
        if code_list:
            decoded_df = decoded_df[decoded_df["code"].isin(code_list)]
        if drop_reit:
            decoded_df = decoded_df[~(decoded_df["market"] == " 東証REIT")]
        if row_more_than:
            dt_count = decoded_df.loc[:, ["code", "dt"]].groupby("code").count().reset_index()
            dt_count = dt_count[dt_count["dt"] >= row_more_than]
            _code_list = list(dt_count["code"].values)
            decoded_df = decoded_df[decoded_df["code"].isin(_code_list)]
        return decoded_df


def _decode_stock_data(_df: pd.DataFrame) -> pd.DataFrame:
    """

    Args:
        _df:

    Returns:

    """
    # 正規表現を利用して数値のみにする
    return (
        _df.assign(
            dt=_df["crawl_datetime"].apply(lambda x: datetime.fromisoformat(x).strftime("%Y-%m-%d")),
        )
        .loc[:, StockInfo.schema()]
        .drop_duplicates()
    )
