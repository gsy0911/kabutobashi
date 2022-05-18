import pandas as pd
import pydantic
import pytest

import kabutobashi as kb
from kabutobashi.domain.errors import KabutobashiEntityError


class TestStockBrand:
    def test_error_init(self):
        with pytest.raises(pydantic.ValidationError):
            _ = kb.StockBrand(
                id=None,
                code="1234",
                market="",
                name="",
                unit="",
                market_capitalization="",
                industry_type="",
                issued_shares="",
            )


class TestStockRecord:
    def test_error_init(self):
        with pytest.raises(pydantic.ValidationError):
            _ = kb.StockRecord(
                id=None,
                code="1234",
                open="",
                high="",
                low="",
                close="",
                psr="",
                per="",
                pbr="",
                volume="",
                dt="",
            )


class TestStockIpo:
    def test_error_init(self):
        with pytest.raises(pydantic.ValidationError):
            _ = kb.StockIpo(
                id=None, code="", manager="", stock_listing_at="", public_offering="", evaluation="", initial_price=""
            )


class TestWeeks52HihLow:
    def test_error_init(self):
        with pytest.raises(pydantic.ValidationError):
            _ = kb.Weeks52HighLow(
                code="", brand_name="", close="", buy_or_sell="", volatility_ratio="", volatility_value=""
            )


class TestStockDataSingleCode:
    def test_of(self, data_path):
        df = pd.read_csv(f"{data_path}/example.csv.gz")
        df["code"] = df["code"].astype(str)
        single_code = df[df["code"] == "1375"]
        _ = kb.StockDataSingleCode.of(df=single_code)

        # check None
        with pytest.raises(KabutobashiEntityError):
            _ = kb.StockDataSingleCode(
                code="-",
                stock_recordset=kb.StockRecordset.of(df=pd.DataFrame()),
                stop_updating=False,
                contains_outlier=False,
                len_=0,
            )

        # check multiple code
        with pytest.raises(KabutobashiEntityError):
            _ = kb.StockDataSingleCode.of(df=df)

        # check invalid column
        with pytest.raises(KabutobashiEntityError):
            _ = kb.StockDataSingleCode.of(df=single_code[["close"]])

    def test_get_df(self, data_path):
        df = pd.read_csv(f"{data_path}/example.csv.gz")
        df["code"] = df["code"].astype(str)
        single_code = df[df["code"] == "1375"]
        sdsc = kb.StockDataSingleCode.of(df=single_code)

        required_cols = ["code", "open", "close", "high", "low", "volume", "per", "psr", "pbr", "dt"]
        optional_cols = ["name", "industry_type", "market", "unit"]

        # check minimum df
        minimum_df = sdsc.to_df()
        assert all([(c in minimum_df.columns) for c in required_cols])
        assert all([(c not in minimum_df.columns) for c in optional_cols])

        # check full df
        full_df = sdsc.to_df(minimum=False)
        assert all([(c in full_df.columns) for c in required_cols])
        assert all([(c in full_df.columns) for c in optional_cols])

        latest_date_df = sdsc.to_df(latest=True)
        assert len(latest_date_df.index) == 1


class TestStockRecordset:
    def test_code_iterable(self):
        records = kb.example()
        for _ in records.to_code_iterable(until=1):
            pass


class TestStockSingleAggregate:
    def test_pass(self):
        records = kb.example()
        methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
        agg = kb.StockCodeSingleAggregate.of(entity=records, code="1375")
        _ = agg.with_processed(methods=methods).with_estimated(estimate_filters=kb.estimate_filters)
