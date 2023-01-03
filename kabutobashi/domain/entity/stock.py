from datetime import datetime
from typing import List, Optional

import jpholiday
import pandas as pd
from pydantic import BaseModel, Field

from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.serialize import ICsvLineSerialize, IDfSerialize, IDictSerialize

from .util import _convert_float, _convert_int

__all__ = ["StockBrand", "StockPriceRecord", "StockReferenceIndicator", "Stock"]


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
            unit=_convert_int(data.get("unit", 0)),
            market=data.get("market"),
            name=data.get("name"),
            industry_type=data.get("industry_type"),
            market_capitalization=data.get("market_capitalization"),
            issued_shares=data.get("issued_shares"),
            is_delisting=data.get("is_delisting", False),
        )

    def to_dict(self) -> dict:
        return self.dict()

    def is_reit(self) -> bool:
        return self.market == "東証REIT"

    def __eq__(self, other):
        if not isinstance(other, StockBrand):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    class Config:
        orm_mode = True


class StockPriceRecord(BaseModel, IDictSerialize, ICsvLineSerialize, IDfSerialize):
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
            open=_convert_float(open),
            high=_convert_float(high),
            low=_convert_float(low),
            close=_convert_float(close),
            volume=_convert_float(volume),
            dt=dt,
        )

    def is_outlier(self) -> bool:
        return self.open == 0 or self.high == 0 or self.low == 0 or self.close == 0

    def to_dict(self) -> dict:
        data = self.dict()
        del data["id"]
        return data

    @staticmethod
    def from_dict(data: dict) -> "StockPriceRecord":

        # TODO ここの日付の処理も何かしら修正する
        data_date = data.get("date")
        data_dt = data.get("dt")
        data_crawl_datetime = data.get("crawl_datetime")

        if data_date and data_dt and data_crawl_datetime:
            raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかしか選べません")
        if data_date:
            dt = data_date
        elif data_dt:
            dt = data_dt
        elif data_crawl_datetime:
            dt = datetime.fromisoformat(data_crawl_datetime).strftime("%Y-%m-%d")
        else:
            raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかが存在しません")

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
            dt=dt,
        )

    @staticmethod
    def from_line(data: str):
        data = {sp_v[0]: sp_v[1] for v in data.split(",") if len(sp_v := v.split("=")) == 2}
        return StockPriceRecord(**data)

    def to_line(self) -> str:
        data = [
            f"id={self.id}",
            f"code={self.code}",
            f"open={self.open}",
            f"high={self.high}",
            f"low={self.low}",
            f"close={self.close}",
            f"volume={self.volume}",
            f"dt={self.dt}",
        ]
        return ",".join(data)

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

    class Config:
        orm_mode = True


class StockReferenceIndicator(BaseModel, IDictSerialize, ICsvLineSerialize):
    """
    Model: Entity
    JP: 参考指標
    """

    id: Optional[int]
    code: str = Field(description="銘柄コード")
    dt: str = Field(description="日付")
    psr: Optional[float] = Field(description="株価売上高倍率:Price to Sales Ratio")
    per: Optional[float] = Field(description="株価収益率:Price Earnings Ratio")
    pbr: Optional[float] = Field(description="株価純資産倍率:Price Book-value Ratio")
    ipo_manager: Optional[str] = Field(description="IPO_主幹")
    ipo_evaluation: Optional[str] = Field(description="IPO_評価")
    stock_listing_at: Optional[str] = Field(description="上場日")
    initial_price: Optional[float] = Field(description="初値")

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
        return self.dict()

    @staticmethod
    def from_dict(data: dict) -> "StockReferenceIndicator":
        return StockReferenceIndicator(
            id=0,
            code=data["code"],
            dt=data["dt"],
            psr=data.get("psr"),
            per=data.get("per"),
            pbr=data.get("pbr"),
        )

    @staticmethod
    def from_line(data: str):
        data = {sp_v[0]: sp_v[1] for v in data.split(",") if len(sp_v := v.split("=")) == 2}
        return StockReferenceIndicator(**data)

    def to_line(self) -> str:
        data = [
            f"id={self.id}",
            f"code={self.code}",
            f"dt={self.dt}",
            f"psr={self.psr}",
            f"per={self.per}",
            f"pbr={self.pbr}",
        ]
        return ",".join(data)


class Stock(BaseModel, IDfSerialize):
    code: str = Field(description="銘柄コード")
    brand: StockBrand = Field(description="銘柄情報")
    daily_price_records: List[StockPriceRecord] = Field(description="日次株価記録", repr=False)
    reference_indicator: StockReferenceIndicator = Field(description="参考指標")
    start_at: str = Field(description="収集開始日")
    end_at: str = Field(description="最新日時")

    def __init__(
        self,
        code: str,
        brand: StockBrand,
        daily_price_records: List[StockPriceRecord],
        reference_indicator: StockReferenceIndicator,
    ):
        dt_list = [v.dt for v in daily_price_records]
        super().__init__(
            code=code,
            brand=brand,
            daily_price_records=daily_price_records,
            reference_indicator=reference_indicator,
            start_at=min(dt_list),
            end_at=max(dt_list),
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
            record_df["is_delisting"] = self.brand.is_delisting
        # from reference-indicator
        if self.reference_indicator.pbr:
            record_df["pbr"] = self.reference_indicator.pbr
        if self.reference_indicator.per:
            record_df["per"] = self.reference_indicator.per
        if self.reference_indicator.psr:
            record_df["psr"] = self.reference_indicator.psr
        return record_df.convert_dtypes().reset_index()

    @staticmethod
    def from_df(data: pd.DataFrame) -> "Stock":
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
