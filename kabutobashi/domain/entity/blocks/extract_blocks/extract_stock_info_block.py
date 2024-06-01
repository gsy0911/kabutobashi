import re
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd
from bs4 import BeautifulSoup

from kabutobashi.domain.services.decode_html.utils import PageDecoder

from ..decorator import block


@block(block_name="extract_stock_info", pre_condition_block_name="crawl_stock_info")
class ExtractStockInfoBlock:
    html_text: str

    def _decode(self, html_text: str) -> dict:
        soup = BeautifulSoup(html_text, features="lxml")
        result: Dict[str, Union[str, bool, int, float, List[str]]] = {}

        stock_board_tag = "md_stockBoard"

        raw_dt = PageDecoder(tag1="span", class1="fsm").decode(bs=soup)
        if isinstance(raw_dt, list):
            raise ValueError()
        pattern = r"\((?P<month>[0-9]+)/(?P<day>[0-9]+)\)|\((?P<hour>[0-9]+):(?P<minute>[0-9]+)\)"
        match_result = re.match(pattern=pattern, string=raw_dt)
        dt = datetime.now()
        if match_result:
            rep = match_result.groupdict()
            if rep.get("month"):
                dt = dt.replace(month=int(rep["month"]))
            if rep.get("day"):
                dt = dt.replace(day=int(rep["day"]))

        # ページ上部の情報を取得
        stock_board = soup.find("div", {"class": stock_board_tag})
        result.update(
            {
                "stock_label": PageDecoder(tag1="div", class1="stock_label").decode(bs=stock_board),
                "name": PageDecoder(tag1="p", class1="md_stockBoard_stockName").decode(bs=stock_board),
                "close": PageDecoder(tag1="div", class1="stock_price").decode(bs=stock_board),
            }
        )

        # ページ中央の情報を取得
        stock_detail = soup.find("div", {"id": "main"})
        info = {}
        for li in stock_detail.find_all("tr", {"class": "ly_vamd"}):
            info[li.find("th").get_text()] = li.find("td").get_text()
        stock_label = str(result.get("stock_label", ""))
        code, market = stock_label.split("  ")
        result.update(
            {
                "dt": dt.strftime("%Y-%m-%d"),
                "code": code,
                "industry_type": PageDecoder(tag1="div", class1="ly_content_wrapper size_ss").decode(bs=stock_detail),
                "market": market,
                "open": info.get("始値", "0"),
                "high": info.get("高値", "0"),
                "low": info.get("安値", "0"),
                "unit": info.get("単元株数", "0"),
                "per": info.get("PER(調整後)", "0"),
                "psr": info.get("PSR", "0"),
                "pbr": info.get("PBR", "0"),
                "volume": info.get("出来高", "0"),
                "market_capitalization": info.get("時価総額", "---"),
                "issued_shares": info.get("発行済株数", "---"),
            }
        )

        return result

    def _process(self) -> pd.DataFrame:
        result = self._decode(html_text=self.html_text)
        # to_df
        df = pd.DataFrame(data=result, index=[result["dt"]])
        return df

    def _validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]):
        keys = series.keys()
        assert "code" in keys, "StockInfoExtractBlockOutput must have 'code' column"
        assert "stock_label" in keys, "StockInfoExtractBlockOutput must have 'stock_label' column"
        assert "name" in keys, "StockInfoExtractBlockOutput must have 'name' column"
        assert "dt" in keys, "StockInfoExtractBlockOutput must have 'dt' column"
        assert "industry_type" in keys, "StockInfoExtractBlockOutput must have 'industry_type' column"
        assert "close" in keys, "StockInfoExtractBlockOutput must have 'close' column"
        assert "market" in keys, "StockInfoExtractBlockOutput must have 'market' column"
        assert "open" in keys, "StockInfoExtractBlockOutput must have 'open' column"
        assert "high" in keys, "StockInfoExtractBlockOutput must have 'high' column"
        assert "low" in keys, "StockInfoExtractBlockOutput must have 'low' column"
        assert "unit" in keys, "StockInfoExtractBlockOutput must have 'unit' column"
        assert "per" in keys, "StockInfoExtractBlockOutput must have 'per' column"
        assert "psr" in keys, "StockInfoExtractBlockOutput must have 'psr' column"
        assert "pbr" in keys, "StockInfoExtractBlockOutput must have 'pbr' column"
        assert "volume" in keys, "StockInfoExtractBlockOutput must have 'volume' column"
        assert "market_capitalization" in keys, "StockInfoExtractBlockOutput must have 'market_capitalization' column"
        assert "issued_shares" in keys, "StockInfoExtractBlockOutput must have 'issued_shares' column"
