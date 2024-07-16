import re
from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
from typing import Dict, List, Union

from kabutobashi.domain.values import (
    DecodeHtmlPageStockInfoMinkabuTop,
    DecodeHtmlPageStockIpo,
    RawHtmlPageStockInfo,
    RawHtmlPageStockIpo,
)

from .utils import IHtmlDecoder, PageDecoder

logger = getLogger(__name__)


@dataclass(frozen=True)
class StockInfoMinkabuTopHtmlDecoder(IHtmlDecoder):
    """
    Model: Service(Implemented)

    Examples:
        >>> from kabutobashi.infrastructure.repository import StockInfoHtmlPageRepository
        >>> # get single page
        >>> html_page = StockInfoHtmlPageRepository(code="0001").read()
        >>> result = StockInfoMinkabuTopHtmlDecoder().decode_to_dict(html_page=html_page)
    """

    def _decode_to_object_hook(self, data: dict) -> DecodeHtmlPageStockInfoMinkabuTop:
        return DecodeHtmlPageStockInfoMinkabuTop.from_dict(data=data)

    def _decode(self, html_page: RawHtmlPageStockInfo) -> dict:
        soup = html_page.get_as_soup()
        result: Dict[str, Union[str, bool, int, float, List[str]]] = {"html": html_page.html}

        stock_board_tag = "md_stockBoard"

        raw_dt = PageDecoder(tag1="span", class1="fsm").decode(bs=soup)
        pattern = r"\((?P<month>[0-9]+)/(?P<day>[0-9]+)\)|\((?P<hour>[0-9]+):(?P<minute>[0-9]+)\)"
        match_result = re.match(pattern, raw_dt)
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


@dataclass(frozen=True)
class StockIpoHtmlDecoder(IHtmlDecoder):
    """
    Model: Service(Implemented)
    """

    def _decode(self, html_page: RawHtmlPageStockIpo) -> dict:
        soup = html_page.get_as_soup()
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

    def _decode_to_object_hook(self, data: dict) -> List[DecodeHtmlPageStockIpo]:
        ipo_list = data["ipo_list"]
        result_list = []
        for v in ipo_list:
            result_list.append(DecodeHtmlPageStockIpo.from_dict(data=v))
        return result_list
