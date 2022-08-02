import pytest

import kabutobashi as kb


def test_crawl_page_detail():
    result = kb.StockRecordsetCrawler.crawl_single(code=4395, dt="2022-07-23")
    assert result is not None
    assert type(result) is dict

    result = kb.StockRecordsetCrawler(code_list=[4395], dt="2022-07-23").read()
    assert result is not None
    assert type(result) is kb.StockRecordset


def test_crawl_ipo_list():
    html_page = kb.StockIpoHtmlPage.of(year="2019")
    result = kb.StockIpoHtmlDecoder(html_page=html_page).decode()
    assert result is not None
    assert type(result) is dict


def test_crawl_week_52_high_low_list():
    html_page = kb.StockWeeks52HighLowHtmlPage.of(data_type="newly_low", dt="2022-07-23")
    result = kb.Weeks52HighLowHtmlDecoder(html_page=html_page).decode()
    assert result is not None
    assert type(result) is dict
