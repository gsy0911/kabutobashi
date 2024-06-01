from typing import Optional

import pandas as pd

from ..decorator import block
from .abc_crawl_block import from_url


@block(block_name="crawl_stock_info")
class CrawlStockInfoBlock:
    code: str

    def _process(self) -> dict:
        html_text = from_url(url=f"https://minkabu.jp/stock/{self.code}")
        return {"code": self.code, "html_text": html_text}

    def _validate_code(self, code: str):
        if code is None:
            raise ValueError()

    def _validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]):
        keys = params.keys()
        assert "code" in keys, "CrawlStockInfoBlockOutput must have 'code' column"
        assert "html_text" in keys, "CrawlStockInfoBlockOutput must have 'html_text' column"
