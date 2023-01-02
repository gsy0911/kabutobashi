import pandas as pd
import pydantic
import pytest

import kabutobashi as kb
from kabutobashi.domain.entity.stock import StockBrand, StockPriceRecord, StockReferenceIndicator
from kabutobashi.domain.errors import KabutobashiEntityError


@pytest.fixture(scope="module", autouse=True)
def entity() -> pd.DataFrame:
    yield kb.example()


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


class TestStockReferenceIndicator:
    def test_pass_init(self):
        _ = StockReferenceIndicator(id=0, code="1234", dt="2023-01-01", pbr=0, psr=0, per=0)
        _ = StockReferenceIndicator.from_dict(
            {"id": 0, "code": "1234", "dt": "2023-01-01", "pbr": 0, "psr": 0, "per": 0}
        )
        _ = StockReferenceIndicator.from_line("id=0,code=1234,dt=2023-01-01,pbr=0,psr=0,per=0")


class TestStockIpo:
    def test_pass_init(self):
        _ = kb.StockIpo(code="", manager="", stock_listing_at="", public_offering=0, evaluation="", initial_price=0)


class TestStock:
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


class TestStockSingleAggregate:
    def test_pass(self, entity: pd.DataFrame):
        methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
        agg = kb.StockCodeSingleAggregate.of(entity=entity, code="1375")
        estimated = agg.with_processed(methods=methods).with_estimated(stock_analysis=kb.stock_analysis)
        value = estimated.weighted_estimated_value({"fundamental": 1.0, "volume": 1.0})
        assert value != 0

        # check visualize single column
        data_visualized = agg.visualize(kb.sma)
        assert data_visualized.fig

        # check visualize multiple columns
        data_visualized = agg.visualize(kb.macd)
        assert data_visualized.fig
