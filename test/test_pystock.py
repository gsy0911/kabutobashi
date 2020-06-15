import pytest
import kabutobashi as ps


@pytest.fixture(scope="module", autouse=True)
def var_stock_df():
    stock_df = ps.example_data()
    yield stock_df


def test_example_data(var_stock_df):
    columns = var_stock_df.columns
    assert "date" in columns
    assert "open" in columns
    assert "close" in columns
    assert "high" in columns
    assert "low" in columns


def test_read_stock_data():
    none_paths = []
    df = ps.read_stock_csv(none_paths)
    assert df is None

    paths = [
        "../data/dt=2020-02-29.csv",
        "../data/dt=2020-03-01.csv"
        ]
    df = ps.read_stock_csv(paths)
    columns = df.columns
    assert "code" in columns
    assert "close" in columns
    assert "open" in columns
    assert "high" in columns
    assert "low" in columns
    assert "per" in columns
    assert "pbr" in columns
    assert "psr" in columns
    assert "unit" in columns
    assert "volume" in columns
    assert "dt" in columns
    assert "market" in columns


def test_analysis_with_sma(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.sma)
    columns = analysis_df.columns
    assert "sma_short" in columns
    assert "sma_medium" in columns
    assert "sma_long" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_macd(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.macd)
    columns = analysis_df.columns
    assert "ema_short" in columns
    assert "ema_long" in columns
    assert "signal" in columns
    assert "macd" in columns
    assert "histogram" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_stochastics(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.stochastics)
    columns = analysis_df.columns
    assert "K" in columns
    assert "D" in columns
    assert "SD" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_adx(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.adx)
    columns = analysis_df.columns
    assert "plus_di" in columns
    assert "minus_di" in columns
    assert "DX" in columns
    assert "ADX" in columns
    assert "ADXR" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_ichimoku(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.ichimoku)
    columns = analysis_df.columns
    assert "line_change" in columns
    assert "line_base" in columns
    assert "proceding_span_1" in columns
    assert "proceding_span_2" in columns
    assert "delayed_span" in columns


def test_analysis_with_momentum(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.momentum)
    columns = analysis_df.columns
    assert "momentum" in columns
    assert "sma_momentum" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_spycho_logical(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.psycho_logical)
    columns = analysis_df.columns
    assert "psycho_line" in columns
    assert "bought_too_much" in columns
    assert "sold_too_much" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_analysis_with_bollinger_bands(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.bollinger_bands)
    columns = analysis_df.columns
    assert "upper_2_sigma" in columns
    assert "lower_2_sigma" in columns
    assert "over_upper_continuity" in columns
    assert "over_lower_continuity" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_get_impact_with(var_stock_df):
    result_1 = ps.get_impact_with(var_stock_df, ps.sma)
    assert "sma" in result_1.keys()
    result_2 = ps.get_impact_with(var_stock_df, [ps.sma, ps.macd])
    assert "sma" in result_2.keys()
    assert "macd" in result_2.keys()


def test_io_read_csv():
    _df = ps.read_csv(1)
    assert _df is None
    _df = ps.read_csv("../data/stooq.csv")
    assert _df is not None
