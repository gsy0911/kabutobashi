import pytest
import pystock as ps


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


def test_analysis_with_sma(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.sma)
    columns = analysis_df.columns
    assert "sma_short" in columns
    assert "sma_medium" in columns
    assert "sma_long" in columns
    assert "buy_signal" in columns
    assert "sell_signal" in columns


def test_visualize_with_sma(var_stock_df):
    fig = ps.visualize_with(var_stock_df, ps.sma)
    assert fig is not None


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


def test_visualize_with_macd(var_stock_df):
    fig = ps.visualize_with(var_stock_df, ps.macd)
    assert fig is not None


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


def test_analysis_with_bollinger_bands(var_stock_df):
    analysis_df = ps.analysis_with(var_stock_df, ps.bollinger_bands)
    columns = analysis_df.columns
    assert "upper_2_sigma" in columns
    assert "lower_2_sigma" in columns
    assert "over_upper_continuity" in columns
    assert "over_lower_continuity" in columns


def test_crawl_page_not_found():
    page = "https://minkabu.jp/stock/994"
    with pytest.raises(ps.errors.CrawlPageNotFoundError):
        bs = ps.get_beautifulsoup_result(page)


def test_crawl_page_detail():
    result = ps.get_stock_detail(4395)
    assert result is not None
    assert type(result) is dict


def test_crawl_ipo_list():
    result = ps.get_ipo_list_from_year(2019)
    assert result is not None
    assert type(result) is dict


def test_io_read_csv():
    _df = ps.read_csv(1)
    assert _df is None
    _df = ps.read_csv("../data/stooq.csv")
    assert _df is not None


def test_version():
    assert ps.__version__ == '0.0.1'
