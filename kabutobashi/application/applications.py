import pandas as pd

from kabutobashi.infrastructure.repository import KabutobashiDatabase


def decode_brand_list(path: str, database_dir: str) -> pd.DataFrame:
    """
    See Also: https://www.jpx.co.jp/markets/statistics-equities/misc/01.html
    """
    df = pd.read_excel(path)
    column_renames = {
        "コード": "code",
        "銘柄名": "name",
        "市場・商品区分": "market",
        "33業種区分": "industry_type",
    }
    df = df.rename(columns=column_renames)
    df = df[column_renames.values()]
    df["market"] = df["market"].apply(lambda x: x.replace("（内国株式）", ""))
    prime_df = df[df["market"] == "プライム"]
    standard_df = df[df["market"] == "スタンダード"]
    growth_df = df[df["market"] == "グロース"]
    merged_df = pd.concat([prime_df, standard_df, growth_df]).reset_index()

    KabutobashiDatabase(database_dir=database_dir).insert_brand_df(df=merged_df)
    return merged_df
