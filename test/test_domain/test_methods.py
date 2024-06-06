import pytest

import kabutobashi as kb


@pytest.fixture(scope="module", autouse=True)
def stock_agg() -> kb.StockCodeSingleAggregate:
    df = kb.example()
    yield kb.StockCodeSingleAggregate.of(entity=df, code="1375")


def test_example_data(stock_agg):
    columns = stock_agg.stock.to_df().columns
    assert "dt" in columns
    assert "open" in columns
    assert "close" in columns
    assert "high" in columns
    assert "low" in columns


@pytest.mark.skip(reason="buy_signal and sell_signal is not implemented")
def test_analysis_with_ichimoku(stock_agg):
    processed = stock_agg.with_processed([kb.ichimoku])
    columns = processed.processed_list[0].df.columns
    assert "line_change" in columns
    assert "line_base" in columns
    assert "proceding_span_1" in columns
    assert "proceding_span_2" in columns
    assert "delayed_span" in columns
    # method name
    assert processed.processed_list[0].applied_method_name == "ichimoku"


def test_analysis_with_fitting(stock_agg):
    processed = stock_agg.with_processed([kb.fitting])
    columns = processed.processed_list[0].df.columns
    assert "linear_fitting" in columns
    assert "square_fitting" in columns
    assert "cube_fitting" in columns
    # method name
    assert processed.processed_list[0].applied_method_name == "fitting"


def test_analysis_with_basic(stock_agg):
    processed = stock_agg.with_processed([kb.basic])
    columns = processed.processed_list[0].df.columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns
    # method name
    assert processed.processed_list[0].applied_method_name == "basic"


def test_analysis_with_pct_change(stock_agg):
    processed = stock_agg.with_processed([kb.pct_change])
    # method name
    assert processed.processed_list[0].applied_method_name == "pct_change"


@pytest.mark.skip(reason="industry_categories is not prepared")
def test_analysis_with_industry_categories(stock_agg):
    processed = stock_agg.with_processed([kb.industry_categories])
    # method name
    assert processed.processed_list[0].applied_method_name == "industry_categories"


def test_analysis_with_volatility(stock_agg):
    processed = stock_agg.with_processed([kb.volatility])
    # method name
    assert processed.processed_list[0].applied_method_name == "volatility"
