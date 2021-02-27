"""
io module provides input/output method
"""

from datetime import datetime
from typing import Union, Optional

import pandas as pd


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
        **kwargs) -> Optional[pd.DataFrame]:
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
            decoded_df = decoded_df[decoded_df['code'].isin(code_list)]
        if drop_reit:
            decoded_df = decoded_df[~(decoded_df['market'] == " 東証REIT")]
        if row_more_than:
            dt_count = decoded_df.loc[:, ["code", "dt"]].groupby("code").count().reset_index()
            dt_count = dt_count[dt_count['dt'] >= row_more_than]
            _code_list = list(dt_count['code'].values)
            decoded_df = decoded_df[decoded_df['code'].isin(_code_list)]
        return decoded_df


def _decode_stock_data(_df: pd.DataFrame) -> pd.DataFrame:
    """
    以下のような株のデータを扱いやすいように整形する関数
    stock_label,name,close,date,industry_type,open,high,low,unit,per,psr,pbr,volume,market_capitalization,issued_shares,crawl_datetime,code
    1436  東証マザーズ,フィット,540.0,株価(15:00),業種建設業,555.0円,557.0円,482.0円,100株,---,0.46倍,0.54倍,"22,000株","2,312百万円","4,282千株",2020-03-13T23:31:04,1436
    1438  名証２部,岐阜造園,"1,098.0",株価(12:38),業種建設業,"1,110.0円","1,150.0円","1,098.0円",100株,9.19倍,0.38倍,0.62倍,"3,100株","1,594百万円","1,451千株",2020-03-13T23:31:06,1438
    :param _df:
    :return:
    """

    # 正規表現を利用して数値のみにする
    _df = _df.assign(
        market=_df['stock_label'].str.extract('[0-9]+ (.+)', expand=False),
        open=_df['open'].str.extract('(.+)円', expand=False),
        high=_df['high'].str.extract('(.+)円', expand=False),
        low=_df['low'].str.extract('(.+)円', expand=False),
        unit=_df['unit'].str.extract('(.+)株', expand=False),
        per=_df['per'].str.extract('(.+)倍', expand=False),
        psr=_df['psr'].str.extract('(.+)倍', expand=False),
        pbr=_df['pbr'].str.extract('(.+)倍', expand=False),
        volume=_df['volume'].str.extract('(.+)株', expand=False),
        dt=_df['crawl_datetime'].apply(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d"))
    )

    # 必要なカラムに絞る
    required_columns = ["code", "open", "close", "high", "low", "unit", "volume", "per", "psr", "pbr", "market", "dt"]
    _df = _df.loc[:, required_columns].drop_duplicates()
    # 変な値はpd.NAに変換
    _df = _df.replace("---", pd.NA)
    return _df
