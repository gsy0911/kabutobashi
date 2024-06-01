from typing import Optional

import pandas as pd

from ..decorator import block
from .abc_crawl_block import from_url


@block(block_name="crawl_stock_ipo")
class CrawlStockIpoBlock:
    year: str

    def _process(self) -> dict:
        html_text = from_url(url=f"https://96ut.com/ipo/list.php?year={self.year}")
        return {"year": self.year, "html_text": html_text}

    def _validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]):
        keys = params.keys()
        assert "year" in keys, "StockIpoCrawlBlockOutput must have 'year' column"
        assert "html_text" in keys, "StockIpoCrawlBlockOutput must have 'html_text' column"
