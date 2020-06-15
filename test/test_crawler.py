import pytest
import kabutobashi as ps


def test_crawl_page_not_found():
    page = "https://minkabu.jp/stock/994"
    with pytest.raises(ps.errors.CrawlPageNotFoundError):
        ps.get_web_page(page)


def test_crawl_page_detail():
    result = ps.get_stock_detail(4395)
    assert result is not None
    assert type(result) is dict


def test_crawl_ipo_list():
    result = ps.get_ipo_list_from_year(2019)
    assert result is not None
    assert type(result) is dict


def test_crawl_week_52_high_low_list():
    result = ps.get_52_weeks_high_low("high")
    assert result is not None
    assert type(result) is dict
