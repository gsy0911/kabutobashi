import kabutobashi as kb


def test_crawl_page_detail():
    result = kb.StockRecordsetCrawler.crawl_single(code=4395)
    assert result is not None
    assert type(result) is dict

    result = kb.StockRecordsetCrawler(code_list=[4395]).read()
    assert result is not None
    assert type(result) is kb.StockRecordset


def test_crawl_ipo_list():
    html_page = kb.StockIpoHtmlPageRepository(year="2019").read()
    result = kb.StockIpoHtmlDecoder().decode(html_page=html_page)
    assert result is not None
    assert type(result) is dict
