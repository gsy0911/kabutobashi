from dataclasses import dataclass

import pandas as pd

from kabutobashi.errors import KabutobashiMethodError

from .method import Method, MethodType


@dataclass(frozen=True)
class IndustryCategories(Method):
    """
    株のvolumeやPBR, PSR, PERなどの値を返す。
    parameterizeのみに利用される。
    """

    method_name: str = "basic"
    method_type: MethodType = MethodType.PARAMETERIZE
    INDUSTRY_TYPE_MAPPING = {
        "水産・農林業": "industry_fisheries_agriculture",
        "鉱業": "industry_mining",
        "建設業": "industry_construction",
        "食料品": "industry_food",
        "繊維製品": "industry_fiber",
        "パルプ・紙": "industry_pulp_paper",
        "化学": "industry_chemistry",
        "医薬品": "industry_pharmaceuticals",
        "石油・石炭製品": "industry_oil_coal",
        "ゴム製品": "industry_rubber",
        "ガラス・土石製品": "industry_glass",
        "鉄鋼": "industry_steel",
        "非鉄金属": "industry_non_ferrous_metals",
        "金属製品": "industry_metal_products",
        "機械": "industry_machine",
        "電気機器": "industry_electric",
        "輸送用機器": "industry_transportation",
        "精密機器": "industry_mechanical_equipment",
        "その他製品": "industry_other",
        "電気・ガス業": "industry_electricity_gas",
        "陸運業": "industry_land_transportation",
        "海運業": "industry_shipping",
        "空運業": "industry_air_freight",
        "倉庫・運輸関連業": "industry_warehouse",
        "情報・通信業": "industry_information",
        "卸売業": "industry_wholesale",
        "小売業": "industry_retail",
        "銀行業": "industry_back",
        "証券、商品先物取引業": "industry_stock_future",
        "保険業": "industry_insurance",
        "その他金融業": "industry_financial",
        "不動産業": "industry_real_state",
        "サービス業": "industry_service",
    }

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df_ = df.copy()
        df_["diff"] = -1
        # 正負が交差した点
        df_ = df_.join(self._cross(df_["diff"]))
        df_ = df_.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df_

    def _color_mapping(self) -> list:
        return []

    def _visualize_option(self) -> dict:
        return {"position": "-"}

    def _processed_columns(self) -> list:
        return []

    def _parameterize(self, df_x: pd.DataFrame, df_p: pd.DataFrame) -> dict:
        params = {v: 0 for v in self.INDUSTRY_TYPE_MAPPING.values()}
        industry_type_list = list(df_x["industry_type"].unique())
        if len(industry_type_list) > 1:
            raise KabutobashiMethodError("industry type should be 1")
        key = industry_type_list[0]
        if key in self.INDUSTRY_TYPE_MAPPING.keys():
            params.update({self.INDUSTRY_TYPE_MAPPING[key]: 1})
        return params
