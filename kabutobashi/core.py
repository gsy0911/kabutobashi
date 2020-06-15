import pandas as pd
from kabutobashi.method.api import Method
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
        **kwargs) -> dict:
    """
    :params stock_df:
    :params method:
    :return: ex: {
            "sma": 0.4,
            "macd": -0.04
        }
    """
    # methodのpipeで渡す際の引数、impactにtrueを渡して直近の各手法の買い・売りの傾向を取得する
    kwargs.update({"impact": "true"})

    # 分析のリスト
    method_list = []
    if type(method) is list:
        method_list.extend(method)
    else:
        method_list.append(method)

    # 結果を格納するdict
    return {str(m): stock_df.pipe(m, **kwargs) for m in method_list}
