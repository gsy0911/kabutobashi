from typing import List

import pandas as pd

from kabutobashi.domain.entity.stock import Stock, StockBrand


def decode_brand_list(path: str) -> List[Stock]:
    """
    See Also: https://www.jpx.co.jp/markets/statistics-equities/misc/01.html
    """
    df = pd.read_excel(path)
    column_renames = {
        "日付": "dt",
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

    stock_list = []
    for idx, row in merged_df.iterrows():
        brand = StockBrand.from_dict(dict(row))
        stock = Stock(code=brand.code, brand=brand, daily_price_records=[], reference_indicator=None)
        stock_list.append(stock)

    return stock_list
