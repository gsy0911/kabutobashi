from kabutobashi.application import crawl_info, crawl_ipo
from kabutobashi.domain.values import StockInfoMinkabuTopPage, StockIpo


class TestStockInfo:
    def test_pass(self):
        res = crawl_info(code="9101")
        assert type(res) is StockInfoMinkabuTopPage


class TestIpo:
    def test_pass(self):
        res = crawl_ipo(year="2022")
        assert type(res) is list
        assert all([(type(v) is StockIpo) for v in res])
