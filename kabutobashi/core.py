import pandas as pd

from kabutobashi.domain.method import Method

# http://www.kabuciao.com/tech/deki/


def analysis_with(stock_df: pd.DataFrame, method: Method) -> pd.DataFrame:
    """

    Args:
        stock_df:
        method:

    Returns:
        pd.DataFrame
    """
    return stock_df.pipe(method)
