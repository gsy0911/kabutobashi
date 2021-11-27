import pytest

import kabutobashi as kb


@pytest.fixture(scope="module", autouse=True)
def var_stock_df():
    sdmc = kb.example()
    sdsc = sdmc.to_single_code(code=1375)
    yield sdsc.df


def test_example_data(var_stock_df):
    columns = var_stock_df.columns
    assert "dt" in columns
    assert "open" in columns
    assert "close" in columns
    assert "high" in columns
    assert "low" in columns


def test_analysis_with_sma(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.sma)
    columns = analysis_df.columns
    assert "sma_short" in columns
    assert "sma_medium" in columns
    assert "sma_long" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_macd(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.macd)
    columns = analysis_df.columns
    assert "ema_short" in columns
    assert "ema_long" in columns
    assert "signal" in columns
    assert "macd" in columns
    assert "histogram" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_stochastics(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.stochastics)
    columns = analysis_df.columns
    assert "K" in columns
    assert "D" in columns
    assert "SD" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_adx(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.adx)
    columns = analysis_df.columns
    assert "plus_di" in columns
    assert "minus_di" in columns
    assert "DX" in columns
    assert "ADX" in columns
    assert "ADXR" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_ichimoku(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.ichimoku)
    columns = analysis_df.columns
    assert "line_change" in columns
    assert "line_base" in columns
    assert "proceding_span_1" in columns
    assert "proceding_span_2" in columns
    assert "delayed_span" in columns


def test_analysis_with_momentum(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.momentum)
    columns = analysis_df.columns
    assert "momentum" in columns
    assert "sma_momentum" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_spycho_logical(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.psycho_logical)
    columns = analysis_df.columns
    assert "psycho_line" in columns
    assert "bought_too_much" in columns
    assert "sold_too_much" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_bollinger_bands(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.bollinger_bands)
    columns = analysis_df.columns
    assert "upper_2_sigma" in columns
    assert "lower_2_sigma" in columns
    assert "over_upper_continuity" in columns
    assert "over_lower_continuity" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


@pytest.mark.skip
def test_analysis_with_fitting(var_stock_df):
    analysis_df = kb.analysis_with(var_stock_df, kb.fitting)
    columns = analysis_df.columns
    assert "linear_fitting" in columns
    assert "square_fitting" in columns
    assert "cube_fitting" in columns


def test_get_impact_with(var_stock_df):
    var_stock_df["code"] = 1
    # var_stock_df["dt"] = var_stock_df["date"]
    result_1 = kb.StockDataProcessed.of(df=var_stock_df, methods=[kb.sma])
    assert "sma" in [v["method"] for v in result_1.processed_dfs]
    result_2 = kb.StockDataProcessed.of(df=var_stock_df, methods=[kb.sma, kb.macd])
    assert "sma" in [v["method"] for v in result_2.processed_dfs]
    assert "macd" in [v["method"] for v in result_2.processed_dfs]
