import pandas as pd
from pystock.method.api import Method
from typing import Union
# http://www.kabuciao.com/tech/deki/


def analysis_with(
        stock_df: pd.DataFrame,
        method: Method) -> pd.DataFrame:
    """
    :params stock_df:
    :params method:
    """
    return stock_df.pipe(method)


def get_impact_with(
        stock_df: pd.DataFrame,
        method: Union[Method, list],
        **kwargs) -> pd.DataFrame:
    """
    :params stock_df:
    :params method:
    """
    kwargs.update({"impact": "true"})

    # 分析のリスト
    method_list = []
    if type(method) is list:
        method_list.extend(method)
    else:
        method_list.append(method)

    # 結果を格納するdict
    result_dict = {}
    for m in method_list:
        result_dict[str(m)] = stock_df.pipe(m, **kwargs)

    return result_dict
