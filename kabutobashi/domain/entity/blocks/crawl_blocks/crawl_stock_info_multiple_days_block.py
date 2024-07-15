from typing import Optional

import pandas as pd

from ..decorator import block
from .abc_crawl_block import from_url


@block(block_name="crawl_stock_info_multiple_days")
class CrawlStockInfoMultipleDaysBlock:
    code: str

    def _process(self) -> dict:
        main_html_text = from_url(url=f"https://minkabu.jp/stock/{self.code}/daily_bar")
        sub_html_text = from_url(url=f"https://minkabu.jp/stock/{self.code}/daily_valuation")
        return {"code": self.code, "main_html_text": main_html_text, "sub_html_text": sub_html_text}

    def _validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]):
        keys = params.keys()
        assert "code" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'code' column"
        assert "main_html_text" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'main_html_text' column"
        assert "sub_html_text" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'sub_html_text' column"


@block(block_name="crawl_stock_info_multiple_days_2")
class CrawlStockInfoMultipleDays2Block:
    code: str
    page: int

    def _process(self) -> dict:
        main_text = from_url(url=f"https://kabutan.jp/stock/kabuka?code={self.code}&ashi=day&page={self.page}")
        return {"code": self.code, "main_html_text": main_text}

    def _validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]):
        keys = params.keys()
        assert "code" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'code' column"
        assert "main_html_text" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'main_html_text' column"
