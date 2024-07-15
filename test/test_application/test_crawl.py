import pandas as pd

from kabutobashi.application import crawl_info, crawl_info_multiple, crawl_ipo


class TestStockInfo:
    def test_pass(self):
        res = crawl_info(code="9101")
        assert type(res) is pd.DataFrame


class TestStockInfoMultiple:
    def test_pass(self):
        res = crawl_info_multiple(code="9101", page="1")
        assert type(res) is pd.DataFrame


class TestIpo:
    def test_pass(self):
        res = crawl_ipo(year="2022")
        assert type(res) is pd.DataFrame
