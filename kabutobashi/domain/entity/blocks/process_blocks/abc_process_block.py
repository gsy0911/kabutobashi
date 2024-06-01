import pandas as pd


def cross(_s: pd.Series, to_plus_name=None, to_minus_name=None) -> pd.DataFrame:
    """
    0を基準としてプラスかマイナスのどちらかに振れたかを判断する関数

    Args:
        _s: 対象のpd.Series
        to_plus_name: 上抜けた場合のカラムの名前
        to_minus_name: 下抜けた場合のカラムの名前
    """
    # shorten variable name
    col = "original"
    shifted = "shifted"

    # shiftしたDataFrameの作成
    shift_s = _s.shift(1)
    df = pd.DataFrame({col: _s, shifted: shift_s})

    # 正負が交差した点
    df = df.assign(
        is_cross=df.apply(lambda x: 1 if x[col] * x[shifted] < 0 else 0, axis=1),
        is_higher=df.apply(lambda x: 1 if x[col] > x[shifted] else 0, axis=1),
        is_lower=df.apply(lambda x: 1 if x[col] < x[shifted] else 0, axis=1),
    )

    # 上抜けか下抜けかを判断している
    df = df.assign(to_plus=df["is_cross"] * df["is_higher"], to_minus=df["is_cross"] * df["is_lower"])
    if to_plus_name is not None:
        df = df.rename(columns={"to_plus": to_plus_name})
    if to_minus_name is not None:
        df = df.rename(columns={"to_minus": to_minus_name})
    return df
