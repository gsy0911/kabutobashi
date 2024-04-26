import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

import jpholiday
import pandas as pd
from pydantic import BaseModel, Field

from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.serialize import IDfSerialize, IDictSerialize
from kabutobashi.utilities import convert_float, convert_int

__all__ = ["Market", "StockBrand", "StockPriceRecord", "StockReferenceIndicator", "Stock"]


class Market(Enum):
    TOKYO_STOCK_EXCHANGE_PRIME = ("東証プライム", "^(東証|東京証券取引所).*?(プライム).*?$")
    TOKYO_STOCK_EXCHANGE_STANDARD = ("東証スタンダード", "^(東証|東京証券取引所).*?(スタンダード).*?$")
    TOKYO_STOCK_EXCHANGE_GROWTH = ("東証グロース", "^(東証|東京証券取引所).*?(グロース).*?$")
    NONE = ("該当無し", "NONE")

    def __init__(self, market_name: str, regex: str):
        self.market_name = market_name
        self.regex = regex

    @staticmethod
    def get(target: Optional[str]):
        if target is None:
            return Market.NONE
        for v in list(Market):
            if re.match(v.regex, target):
                return v
        return Market.NONE


class StockBrand(BaseModel, IDictSerialize):
    """
    Model: Entity
    JP: 銘柄
    """

    id: int = Field(description="id")
    code: str = Field(description="銘柄コード")
    unit: Optional[int] = Field(description="単位")
    market: Optional[str] = Field(description="市場")
    name: Optional[str] = Field(description="銘柄名")
    industry_type: Optional[str] = Field(description="業種")
    market_capitalization: Optional[str] = Field(description="時価総額")
    issued_shares: Optional[str] = Field(description="発行済み株式")
    is_delisting: bool = Field(description="上場廃止")

    def __init__(
        self,
        code: str,
        id: Optional[int] = None,
        unit: Optional[int] = None,
        market: Optional[str] = None,
        name: Optional[str] = None,
        industry_type: Optional[str] = None,
        market_capitalization: Optional[str] = None,
        issued_shares: Optional[str] = None,
        is_delisting: bool = False,
    ):
        # code may "100.0"
        code = code.split(".")[0]

        super().__init__(
            id=0 if id is None else id,
            code=code,
            unit=unit,
            market=market,
            name=name,
            industry_type=industry_type,
            market_capitalization=market_capitalization,
            issued_shares=issued_shares,
            is_delisting=is_delisting,
        )

    @staticmethod
    def from_dict(data: dict) -> "StockBrand":
        code = str(data["code"]).split(".")[0]

        return StockBrand(
            id=data.get("id"),
            code=code,
            unit=convert_int(data.get("unit", 0)),
            market=Market.get(target=data.get("market")).market_name,
            name=data.get("name"),
            industry_type=data.get("industry_type"),
            market_capitalization=data.get("market_capitalization"),
            issued_shares=data.get("issued_shares"),
            is_delisting=data.get("is_delisting", False),
        )

    def to_dict(self) -> dict:
        return self.model_dump()

    def __eq__(self, other):
        if not isinstance(other, StockBrand):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    def __add__(self, other: "StockBrand") -> "StockBrand":
        if other is None:
            return self
        if type(other) is not StockBrand:
            raise KabutobashiEntityError()
        if self.code != other.code:
            raise KabutobashiEntityError()
        return StockBrand(
            code=self.code if self.code is not None else other.code,
            unit=self.unit if self.unit is not None else other.unit,
            market=self.market if self.market is not None else other.market,
            industry_type=self.industry_type if self.industry_type is not None else other.industry_type,
            market_capitalization=(
                self.market_capitalization if self.market_capitalization is not None else other.market_capitalization
            ),
            name=self.name if self.name is not None else other.name,
            issued_shares=self.issued_shares if self.issued_shares is not None else other.issued_shares,
            is_delisting=self.is_delisting or other.is_delisting,
        )

    # TODO modify
    # class Config:
    #     orm_mode = True


class StockPriceRecord(BaseModel, IDictSerialize, IDfSerialize):
    """
    Model: Entity
    JP: 日次株価
    """

    id: int = Field(description="id")
    code: str = Field(description="銘柄コード")
    dt: str = Field(description="日付")
    open: float = Field(description="始値")
    high: float = Field(description="高値")
    low: float = Field(description="底値")
    close: float = Field(description="終値")
    volume: int = Field(description="出来高")

    def __init__(
        self,
        id: Optional[int],
        code: str,
        dt: str,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
    ):

        super().__init__(
            id=0 if id is None else id,
            code=code,
            open=convert_float(open),
            high=convert_float(high),
            low=convert_float(low),
            close=convert_float(close),
            volume=convert_float(volume),
            dt=dt,
        )

    def is_outlier(self) -> bool:
        return self.open == 0 or self.high == 0 or self.low == 0 or self.close == 0

    def to_dict(self) -> dict:
        data = self.model_dump(exclude={"id"})
        return data

    @staticmethod
    def from_dict(data: dict) -> "StockPriceRecord":
        # code may "100.0"
        code = str(data["code"]).split(".")[0]
        return StockPriceRecord(
            id=data.get("id"),
            code=code,
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            volume=data["volume"],
            dt=data["dt"],
        )

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame([self.to_dict()])

    @staticmethod
    def from_df(data: pd.DataFrame) -> List["StockPriceRecord"]:
        required_cols = ["open", "high", "low", "close", "code", "dt", "volume"]
        if set(required_cols) - set(data.columns):
            raise ValueError()
        if len(set(data["code"])) != 1:
            raise ValueError()

        records = []
        for _, row in data.iterrows():
            record = StockPriceRecord.from_dict(row)
            if record.is_valid_date():
                records.append(record)
        return records

    def is_valid_date(self) -> bool:
        return not jpholiday.is_holiday(datetime.strptime(self.dt, "%Y-%m-%d"))

    def __eq__(self, other):
        if not isinstance(other, StockPriceRecord):
            return False
        return self.code == other.code and self.dt == other.dt

    def __hash__(self):
        return hash(self.code)

    # TODO update
    # class Config:
    #     orm_mode = True


class StockReferenceIndicator(BaseModel, IDictSerialize):
    """
    Model: Entity
    JP: 参考指標
    """

    id: Optional[int]
    code: str = Field(description="銘柄コード")
    dt: str = Field(description="日付")
    psr: Optional[float] = Field(description="株価売上高倍率:Price to Sales Ratio", default=None)
    per: Optional[float] = Field(description="株価収益率:Price Earnings Ratio", default=None)
    pbr: Optional[float] = Field(description="株価純資産倍率:Price Book-value Ratio", default=None)
    ipo_manager: Optional[str] = Field(description="IPO_主幹", default=None)
    ipo_evaluation: Optional[str] = Field(description="IPO_評価", default=None)
    stock_listing_at: Optional[str] = Field(description="上場日", default=None)
    initial_price: Optional[float] = Field(description="初値", default=None)

    def __init__(self, id: int, code: str, dt: str, psr: Optional[float], per: Optional[float], pbr: Optional[float]):
        super().__init__(
            id=id,
            code=code,
            dt=dt,
            psr=psr,
            per=per,
            pbr=pbr,
        )

    def to_dict(self) -> dict:
        return self.model_dump()

    @staticmethod
    def from_dict(data: dict) -> "StockReferenceIndicator":
        return StockReferenceIndicator(
            id=0,
            code=data["code"],
            dt=data["dt"],
            psr=convert_float(data.get("psr")),
            per=convert_float(data.get("per")),
            pbr=convert_float(data.get("pbr")),
        )

    def __add__(self, other: "StockReferenceIndicator") -> "StockReferenceIndicator":
        if other is None:
            return self
        if type(other) is not StockReferenceIndicator:
            raise KabutobashiEntityError()
        if self.code != other.code:
            raise KabutobashiEntityError()
        return StockReferenceIndicator(
            id=self.id,
            code=self.code,
            dt=self.dt,
            psr=self.psr if self.psr is not None else other.psr,
            pbr=self.pbr if self.pbr is not None else other.pbr,
            per=self.per if self.per is not None else other.per,
        )


class Stock(BaseModel, IDfSerialize):
    """
    Model: Entity
    JP: 株
    """

    code: str = Field(description="銘柄コード")
    brand: StockBrand = Field(description="銘柄情報")
    daily_price_records: List[StockPriceRecord] = Field(description="日次株価記録", repr=False)
    reference_indicator: Optional[StockReferenceIndicator] = Field(description="参考指標")
    start_at: Optional[str] = Field(description="収集開始日")
    end_at: Optional[str] = Field(description="最新日時")

    def __init__(
        self,
        code: str,
        brand: StockBrand,
        daily_price_records: List[StockPriceRecord],
        reference_indicator: Optional[StockReferenceIndicator],
    ):
        if code != brand.code:
            raise KabutobashiEntityError()
        if reference_indicator is not None:
            if code != reference_indicator.code:
                raise KabutobashiEntityError()
        records_code_list = list(set([v.code for v in daily_price_records]))
        if len(records_code_list) > 1:
            raise KabutobashiEntityError()
        if records_code_list:
            if code != records_code_list[0]:
                raise KabutobashiEntityError()

        dt_list = [v.dt for v in daily_price_records]
        super().__init__(
            code=code,
            brand=brand,
            daily_price_records=daily_price_records,
            reference_indicator=reference_indicator,
            start_at=min(dt_list) if dt_list else None,
            end_at=max(dt_list) if dt_list else None,
        )

    def to_df(self, add_brand=False) -> pd.DataFrame:
        record_df = pd.concat([r.to_df() for r in self.daily_price_records])
        if add_brand:
            # from brand
            if self.brand.industry_type:
                record_df["industry_type"] = self.brand.industry_type
            if self.brand.market:
                record_df["market"] = self.brand.market
            if self.brand.market_capitalization:
                record_df["market_capitalization"] = self.brand.market_capitalization
            if self.brand.name:
                record_df["name"] = self.brand.name
            if self.brand.industry_type:
                record_df["industry_type"] = self.brand.industry_type
            if self.brand.issued_shares:
                record_df["issued_shares"] = self.brand.issued_shares
            if self.brand.unit:
                record_df["unit"] = self.brand.unit
            record_df["is_delisting"] = self.brand.is_delisting
        # from reference-indicator
        if self.reference_indicator.pbr:
            record_df["pbr"] = self.reference_indicator.pbr
        if self.reference_indicator.per:
            record_df["per"] = self.reference_indicator.per
        if self.reference_indicator.psr:
            record_df["psr"] = self.reference_indicator.psr
        return record_df.convert_dtypes().reset_index(drop=True)

    @staticmethod
    def from_df(data: pd.DataFrame) -> "Stock":
        data = data.reset_index(drop=True)
        required_cols = ["open", "high", "low", "close", "code", "dt", "volume"]
        if set(required_cols) - set(data.columns):
            raise KabutobashiEntityError()
        if len(set(data["code"])) != 1:
            raise KabutobashiEntityError()

        code = str(data["code"][0])
        daily_price_records = StockPriceRecord.from_df(data=data)
        latest_dt = max(data["dt"])
        latest_info = data[data["dt"] == latest_dt].to_dict(orient="records")[0]
        latest_info.update({"code": code})
        return Stock(
            code=code,
            brand=StockBrand.from_dict(data=latest_info),
            daily_price_records=daily_price_records,
            reference_indicator=StockReferenceIndicator.from_dict(data=latest_info),
        )

    def contains_outlier(self) -> bool:
        return any([v.is_outlier() for v in self.daily_price_records])

    @staticmethod
    def reduce(stocks: List["Stock"]) -> "Stock":
        code_list = list(set([v.code for v in stocks]))
        if len(code_list) > 1:
            raise KabutobashiEntityError()
        merge_target = stocks[0]
        for v in stocks[1:]:
            merge_target = merge_target + v
        return merge_target

    def __add__(self, other: "Stock") -> "Stock":
        if other is None:
            return self
        if type(other) is not Stock:
            raise KabutobashiEntityError()
        if self.code != other.code:
            raise KabutobashiEntityError()
        daily_price_records = []
        if self.daily_price_records:
            daily_price_records.extend(self.daily_price_records)
        if other.daily_price_records:
            daily_price_records.extend(other.daily_price_records)

        return Stock(
            code=self.code,
            brand=self.brand + other.brand,
            daily_price_records=list(set(daily_price_records)),
            reference_indicator=self.reference_indicator + other.reference_indicator,
        )
