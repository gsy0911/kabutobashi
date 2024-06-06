import pandas as pd
import pydantic
import pytest

import kabutobashi as kb
from kabutobashi.domain.entity.stock import Market, StockBrand, StockPriceRecord, StockReferenceIndicator
from kabutobashi.domain.errors import KabutobashiEntityError


@pytest.fixture(scope="module", autouse=True)
def entity() -> pd.DataFrame:
    yield kb.example()


class TestMarket:
    def test_get(self):
        assert Market.get(target="") is Market.NONE
        assert Market.get(target="東証プライ") is Market.NONE
        assert Market.get(target="東証スタンダー") is Market.NONE
        assert Market.get(target="東証グロー") is Market.NONE
        assert Market.get(target=None) is Market.NONE
        assert Market.get(target="東証プライム") is Market.TOKYO_STOCK_EXCHANGE_PRIME
        assert Market.get(target="東証スタンダード") is Market.TOKYO_STOCK_EXCHANGE_STANDARD
        assert Market.get(target="東証グロース") is Market.TOKYO_STOCK_EXCHANGE_GROWTH


class TestStockBrand:
    def test_error_init(self):
        # type-error
        with pytest.raises(pydantic.ValidationError):
            _ = StockBrand(
                id=None,
                code="1234",
                market="東証",
                name="例",
                unit="",
                market_capitalization="",
                industry_type="",
                issued_shares="",
            )

    def test_init(self):
        brand = StockBrand(
            id=None,
            code="1234",
            market="東証",
            name="例",
            unit=100,
            market_capitalization="",
            industry_type="",
            issued_shares="",
        )
        brand_dict = brand.to_dict()
        assert type(brand_dict) == dict
        assert brand_dict["code"] == "1234"
        assert brand_dict["market"] == "東証"
        assert brand_dict["name"] == "例"
        assert brand_dict["unit"] == 100

    def test_merge_error(self):
        brand1 = StockBrand(
            id=None,
            code="1234",
            market="東証",
            name="例",
            unit=100,
            market_capitalization="",
            industry_type="",
            issued_shares="",
        )
        brand2 = StockBrand(
            id=None,
            code="1235",
            market="東証",
            name="例",
            unit=100,
            market_capitalization="",
            industry_type="",
            issued_shares="",
        )
        with pytest.raises(KabutobashiEntityError):
            _ = brand1 + brand2
        with pytest.raises(KabutobashiEntityError):
            _ = brand1 + ""

    def test_merge_pass(self):
        brand1 = StockBrand(
            id=None,
            code="1234",
            market="東証",
            name="例",
            unit=100,
            market_capitalization=None,
            industry_type=None,
            issued_shares=None,
        )
        merged = brand1 + None
        assert merged.code == "1234"

        brand2 = StockBrand(
            id=None,
            code="1234",
            market="東証",
            name=None,
            unit=None,
            market_capitalization="時価総額",
            industry_type="業種",
            issued_shares="発行済み株式数",
        )
        merged = brand1 + brand2
        assert merged.code == "1234"
        assert merged.name == "例"
        assert merged.market == "東証"
        assert merged.unit == 100
        assert merged.market_capitalization == "時価総額"
        assert merged.industry_type == "業種"
        assert merged.issued_shares == "発行済み株式数"
        merged = brand2 + brand1
        assert merged.code == "1234"
        assert merged.name == "例"
        assert merged.market == "東証"
        assert merged.unit == 100
        assert merged.market_capitalization == "時価総額"
        assert merged.industry_type == "業種"
        assert merged.issued_shares == "発行済み株式数"


class TestStockRecord:
    def test_pass_init(self):
        _ = StockPriceRecord(
            id=None,
            code="1234",
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            dt="",
        )

    def test_eq_test(self):
        price1 = StockPriceRecord(
            id=None,
            code="1234",
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            dt="2022-01-01",
        )
        price2 = StockPriceRecord(
            id=None,
            code="1234",
            open=1,
            high=1,
            low=1,
            close=1,
            volume=1,
            dt="2022-01-01",
        )
        price3 = StockPriceRecord(
            id=None,
            code="1235",
            open=2,
            high=2,
            low=2,
            close=2,
            volume=2,
            dt="2022-01-01",
        )
        price4 = StockPriceRecord(
            id=None,
            code="1234",
            open=3,
            high=3,
            low=3,
            close=3,
            volume=3,
            dt="2022-01-02",
        )
        assert price1 == price2
        assert price1 != price3
        assert price2 != price3
        assert price1 != price4
        assert price2 != price4
        assert price3 != price4
        assert price1 != ""
        assert price2 != ""
        assert price3 != ""
        assert price4 != ""


class TestStockReferenceIndicator:
    def test_pass_init(self):
        _ = StockReferenceIndicator(id=0, code="1234", dt="2023-01-01", pbr=0, psr=0, per=0)
        _ = StockReferenceIndicator.from_dict(
            {"id": 0, "code": "1234", "dt": "2023-01-01", "pbr": 0, "psr": 0, "per": 0}
        )

    def test_error_merge(self):
        reference1 = StockReferenceIndicator(id=0, code="1234", dt="2023-01-01", pbr=0, psr=0, per=0)
        reference2 = StockReferenceIndicator(id=0, code="1235", dt="2023-01-01", pbr=0, psr=0, per=0)
        with pytest.raises(KabutobashiEntityError):
            _ = reference1 + reference2
        with pytest.raises(KabutobashiEntityError):
            _ = reference1 + ""

    def test_pass_merge(self):
        reference1 = StockReferenceIndicator(id=0, code="1234", dt="2023-01-01", pbr=None, psr=None, per=None)
        reference2 = StockReferenceIndicator(id=0, code="1234", dt="2023-01-01", pbr=1, psr=2, per=3)
        merge = reference1 + None
        assert merge.code == "1234"
        merge = reference1 + reference2
        assert merge.code == "1234"
        assert merge.dt == "2023-01-01"
        assert merge.pbr == 1
        assert merge.psr == 2
        assert merge.per == 3


class TestStockIpo:
    def test_pass_init(self):
        _ = kb.DecodeHtmlPageStockIpo(
            code="", manager="", stock_listing_at="", public_offering=0, evaluation="", initial_price=0
        )


class TestStock:
    def test_init_error(self):
        brand = StockBrand(
            id=None,
            code="1234",
            market="東証",
            name="例",
            unit=100,
            market_capitalization=None,
            industry_type=None,
            issued_shares=None,
        )
        brand_e = StockBrand(
            id=None,
            code="1235",
            market="東証",
            name="例",
            unit=100,
            market_capitalization=None,
            industry_type=None,
            issued_shares=None,
        )
        price = StockPriceRecord(
            id=None,
            code="1234",
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            dt="2022-01-01",
        )
        price_e = StockPriceRecord(
            id=None,
            code="1235",
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            dt="2022-01-01",
        )
        reference = StockReferenceIndicator(id=0, code="1234", dt="2023-01-01", pbr=None, psr=None, per=None)
        reference_e = StockReferenceIndicator(id=0, code="1235", dt="2023-01-01", pbr=None, psr=None, per=None)
        with pytest.raises(KabutobashiEntityError):
            _ = kb.Stock(code="1234", brand=brand_e, daily_price_records=[price], reference_indicator=reference)
        with pytest.raises(KabutobashiEntityError):
            _ = kb.Stock(code="1234", brand=brand, daily_price_records=[price_e], reference_indicator=reference)
        with pytest.raises(KabutobashiEntityError):
            _ = kb.Stock(code="1234", brand=brand, daily_price_records=[price, price_e], reference_indicator=reference)
        with pytest.raises(KabutobashiEntityError):
            _ = kb.Stock(code="1234", brand=brand, daily_price_records=[price], reference_indicator=reference_e)

    def test_df_error(self, entity: pd.DataFrame):
        with pytest.raises(KabutobashiEntityError):
            _ = kb.Stock.from_df(data=entity)

    def test_df_pass(self, entity: pd.DataFrame):
        stock = kb.Stock.from_df(data=entity[entity["code"] == 1375])
        stock_df = stock.to_df(add_brand=True)
        stock_df_columns = stock_df.columns
        assert "industry_type" in stock_df_columns
        assert "market" in stock_df_columns
        assert "name" in stock_df_columns
        assert "is_delisting" in stock_df_columns
        assert "pbr" in stock_df_columns
        assert "per" in stock_df_columns
        assert "psr" in stock_df_columns

    def test_merge_error(self):
        brand = StockBrand(
            id=None,
            code="1234",
            market="東証",
            name="例",
            unit=100,
            market_capitalization=None,
            industry_type=None,
            issued_shares=None,
        )
        price = StockPriceRecord(
            id=None,
            code="1234",
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            dt="2022-01-01",
        )
        reference = StockReferenceIndicator(id=0, code="1234", dt="2023-01-01", pbr=None, psr=None, per=None)
        stock = kb.Stock(code="1234", brand=brand, daily_price_records=[price], reference_indicator=reference)
        with pytest.raises(KabutobashiEntityError):
            _ = stock + ""

        # 異なるcode
        brand_2 = StockBrand(
            id=None,
            code="1235",
            market="東証",
            name="例",
            unit=100,
            market_capitalization=None,
            industry_type=None,
            issued_shares=None,
        )
        price_2 = StockPriceRecord(
            id=None,
            code="1235",
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            dt="2022-01-01",
        )
        reference_2 = StockReferenceIndicator(id=0, code="1235", dt="2023-01-01", pbr=None, psr=None, per=None)
        stock_2 = kb.Stock(code="1235", brand=brand_2, daily_price_records=[price_2], reference_indicator=reference_2)
        with pytest.raises(KabutobashiEntityError):
            _ = stock + stock_2

    def test_merge_pass(self):
        brand = StockBrand(
            id=None,
            code="1234",
            market="東証",
            name="例",
            unit=100,
            market_capitalization=None,
            industry_type=None,
            issued_shares=None,
        )
        price = StockPriceRecord(
            id=None,
            code="1234",
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            dt="2022-01-01",
        )
        reference = StockReferenceIndicator(id=0, code="1234", dt="2023-01-01", pbr=None, psr=None, per=None)
        stock = kb.Stock(code="1234", brand=brand, daily_price_records=[price], reference_indicator=reference)
        merge = stock + None
        assert merge.code == "1234"

        merge = stock + stock
        assert merge.code == "1234"
        assert len(merge.daily_price_records) == 1

    def test_reduce_error(self, entity: pd.DataFrame):
        stock1 = kb.Stock.from_df(data=entity[entity["code"] == 1375])
        stock2 = kb.Stock.from_df(data=entity[entity["code"] == 1439])
        with pytest.raises(KabutobashiEntityError):
            kb.Stock.reduce(stocks=[stock1, stock2])

    def test_reduce_pass(self, entity: pd.DataFrame):
        filtered_entity = entity[entity["code"] == 1375]
        stock1 = kb.Stock.from_df(data=filtered_entity[:10])
        stock2 = kb.Stock.from_df(data=filtered_entity[10:])
        stock3 = kb.Stock.from_df(data=filtered_entity)

        assert len(kb.Stock.reduce(stocks=[stock1, stock2]).daily_price_records) == len(stock3.daily_price_records)
