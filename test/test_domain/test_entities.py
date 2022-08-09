import pydantic
import pytest

import kabutobashi as kb
from kabutobashi.domain.errors import KabutobashiEntityError


@pytest.fixture(scope="module", autouse=True)
def example_records() -> kb.StockRecordset:
    yield kb.example()


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
                is_delisting=False,
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


class TestStockRecordset:
    def test_code_iterable(self, example_records: kb.StockRecordset):
        for _ in example_records.to_code_iterable(until=1):
            pass

    def test_multiple_code_error(self, example_records: kb.StockRecordset):
        with pytest.raises(KabutobashiEntityError):
            _ = example_records.get_single_code_recordset_status()

    def test_invalid_column_error(self, example_records: kb.StockRecordset):
        # check invalid column
        with pytest.raises(KabutobashiEntityError):
            _ = kb.StockRecordset.of(df=example_records.to_df()[["close"]])

    def test_get_df(self, example_records: kb.StockRecordset):
        records = example_records.to_single_code(code="1375")

        required_cols = ["code", "open", "close", "high", "low", "volume", "per", "psr", "pbr", "dt"]
        optional_cols = ["name", "industry_type", "market", "unit"]

        # check minimum df
        minimum_df = records.to_df()
        assert all([(c in minimum_df.columns) for c in required_cols])
        assert all([(c not in minimum_df.columns) for c in optional_cols])

        # check full df
        full_df = records.to_df(minimum=False)
        assert all([(c in full_df.columns) for c in required_cols])
        assert all([(c in full_df.columns) for c in optional_cols])

        latest_date_df = records.to_df(latest=True)
        assert len(latest_date_df.index) == 1

        status = records.get_single_code_recordset_status()
        assert status.code == "1375"


class TestStockSingleAggregate:
    def test_pass(self, example_records: kb.StockRecordset):
        methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
        agg = kb.StockCodeSingleAggregate.of(entity=example_records, code="1375")
        estimated = agg.with_processed(methods=methods).with_estimated(estimate_filters=kb.estimate_filters)
        value = estimated.weighted_estimated_value({"fundamental": 1.0, "volume": 1.0})
        assert value != 0

        # check visualize single column
        data_visualized = agg.visualize(kb.sma)
        assert data_visualized.fig

        # check visualize multiple columns
        data_visualized = agg.visualize(kb.macd)
        assert data_visualized.fig
