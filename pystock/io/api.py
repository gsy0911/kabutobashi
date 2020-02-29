from typing import Union
import pandas as pd


def example_data() -> pd.DataFrame:
    data_path_list = ["../data/stooq.csv"]
    _df = read_csv(data_path_list)
    _df = _df.sort_values("date", ascending=True)
    _df = _df.convert_dtypes()
    return _df


def read_csv(path_candidate: Union[str, list]) -> Union[pd.DataFrame, None]:
    if type(path_candidate) is str:
        return pd.read_csv(path_candidate)
    elif type(path_candidate) is list:
        df_list = [pd.read_csv(p) for p in path_candidate]
        return pd.concat(df_list)
    else:
        return None
