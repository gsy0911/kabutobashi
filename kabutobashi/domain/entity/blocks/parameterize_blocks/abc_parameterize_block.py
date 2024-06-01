import pandas as pd


def get_impact(df: pd.DataFrame, influence: int, tail: int, prefix: str = "") -> float:
    """
    売りと買いのシグナルの余波の合計値を返す。

    Args:
        df:
        influence:
        tail:

    Returns:
        [-1,1]の値をとる。-1: 売り、1: 買いを表す
    """
    columns = df.columns
    if "buy_signal" not in columns and f"{prefix}_buy_signal" not in columns:
        return 0
    if "sell_signal" not in columns and f"{prefix}_sell_signal" not in columns:
        return 0

    if "buy_signal" in columns:
        df["buy_impact"] = df["buy_signal"].ewm(span=influence).mean()
    elif f"{prefix}_buy_signal" in columns:
        df["buy_impact"] = df[f"{prefix}_buy_signal"].ewm(span=influence).mean()

    if "sell_signal" in columns:
        df["sell_impact"] = df["sell_signal"].ewm(span=influence).mean()
    elif f"{prefix}_sell_signal" in columns:
        df["sell_impact"] = df[f"{prefix}_sell_signal"].ewm(span=influence).mean()

    buy_impact_index = df["buy_impact"].iloc[-tail:].sum()
    sell_impact_index = df["sell_impact"].iloc[-tail:].sum()
    return round(buy_impact_index - sell_impact_index, 5)
