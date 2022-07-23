import pytest

import kabutobashi as kb


def test_crawl_page_detail():
    result = kb.crawl_single(code=4395, dt="2022-07-23")
    assert result is not None
    assert type(result) is dict


def test_crawl_ipo_list():
    result = kb.StockIpoPage(year=2019).get()
    assert result is not None
    assert type(result) is dict


@pytest.mark.skip(reason="page changed")
def test_crawl_week_52_high_low_list():
    result = kb.Weeks52HighLowPage(data_type="high").get()
    assert result is not None
    assert type(result) is dict
