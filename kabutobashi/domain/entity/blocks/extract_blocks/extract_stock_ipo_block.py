from typing import Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup

from kabutobashi.domain.values import DecodeHtmlPageStockIpo

from ..decorator import block


@block(block_name="extract_stock_ipo", pre_condition_block_name="crawl_stock_ipo")
class ExtractStockIpoBlock:
    html_text: str

    def _decode(self, html_text: str) -> dict:
        soup = BeautifulSoup(html_text, features="lxml")
        table_content = soup.find("div", {"class": "tablewrap"})
        table_thead = table_content.find("thead")
        # headの取得
        table_head_list = []
        for th in table_thead.find_all("th"):
            table_head_list.append(th.get_text())

        # bodyの取得
        table_tbody = table_content.find("tbody")
        whole_result = []
        for idx, tr in enumerate(table_tbody.find_all("tr")):
            table_body_dict = {}
            for header, td in zip(table_head_list, tr.find_all("td")):
                table_body_dict[header] = td.get_text().replace("\n", "")
            whole_result.append(DecodeHtmlPageStockIpo.from_dict(data=table_body_dict).to_dict())
        return {"ipo_list": whole_result}

    def _process(self) -> Tuple[pd.DataFrame, dict]:
        # to_df
        result = self._decode(html_text=self.html_text)
        df = pd.DataFrame(data=result["ipo_list"])
        return df, result

    def _validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]):
        keys = series.keys()
        # assert "ipo_list" in keys, "StockIpoExtractBlockOutput must have 'ipo_list' column"
