import pandas as pd
from pystock.method.api import Method


def analysis_with(
        stock_df: pd.DataFrame,
        method: Method) -> pd.DataFrame:
    """
    :params stock_df:
    :params method:
    """
    return stock_df.pipe(method)


def visualize_with(
        stock_df: pd.DataFrame,
        method: Method,
        visualize_start: str = None,
        visualize_end: str = None):
    """
    :params stock_df:
    :params method:
    :params visualize_start:
    :params visualize_end:
    """
    # figにするのは確定
    param_dict = {"to_fig": True}
    if visualize_start is not None:
        param_dict['visualize_start'] = visualize_start
    if visualize_end is not None:
        param_dict['visualize_end'] = visualize_end
    return stock_df.pipe(method, **param_dict)
