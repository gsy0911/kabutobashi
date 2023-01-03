import kabutobashi as kb
from kabutobashi.domain.services.decode_html import StockInfoMinkabuTopHtmlDecoder, StockIpoHtmlDecoder
from kabutobashi.domain.values import StockInfoMinkabuTopPage
from kabutobashi.infrastructure.repository import StockInfoHtmlPageRepository


def test_crawl_page_detail():
    html_repo = StockInfoHtmlPageRepository(code=4395)
    html_page = html_repo.read()
    result = StockInfoMinkabuTopHtmlDecoder().decode_to_dict(html_page=html_page)
    assert result is not None
    assert type(result) is dict

    result_object = StockInfoMinkabuTopHtmlDecoder().decode_to_object(html_page=html_page)
    assert result_object is not None
    assert type(result_object) is StockInfoMinkabuTopPage


def test_crawl_ipo_list():
    html_page = kb.StockIpoHtmlPageRepository(year="2019").read()
    result = StockIpoHtmlDecoder().decode_to_dict(html_page=html_page)
    assert result is not None
    assert type(result) is dict
