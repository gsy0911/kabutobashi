import pytest
import kabutobashi as kb


def test_crawl_page_not_found():
    page = "https://minkabu.jp/stock/994"
    with pytest.raises(ps.errors.CrawlPageNotFoundError):
        ps.get_web_page(page)


def test_crawl_page_detail():
    result = kb.StockInfoPage(code=4395).get()
    assert result is not None
    assert type(result) is dict


def test_crawl_ipo_list():
    result = kb.StockIpoPage(year=2019).get()
    assert result is not None
    assert type(result) is dict


def test_crawl_week_52_high_low_list():
    result = kb.Weeks52HighLowPage(data_type="high").get()
    assert result is not None
    assert type(result) is dict
