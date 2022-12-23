from dataclasses import dataclass
from logging import getLogger
from typing import Dict, List, Union
from datetime import datetime

from kabutobashi.domain.values import StockInfoHtmlPage, StockInfoMinkabuTopPage

from .utils import IHtmlDecoder, PageDecoder

logger = getLogger(__name__)


@dataclass(frozen=True)
class StockInfoMinkabuTopHtmlDecoder(IHtmlDecoder):
    """
    Examples:
        >>> import kabutobashi as kb
        >>> # get single page
        >>> page_html = kb.StockInfoHtmlPageRepository(code="0001", dt="2022-07-22").read()
        >>> result = StockInfoMinkabuTopHtmlDecoder().decode_to_dict(page_html=page_html)
    """

    def _decode_to_object_hook(self, data: dict) -> StockInfoMinkabuTopPage:
        return StockInfoMinkabuTopPage(
            code=data["code"],
            dt=data["dt"],
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            pbr=data["pbr"],
            per=data["per"],
            psr=data["psr"],
            unit=data["unit"],
            volume=data["volume"],
            market=data["market"],
            market_capitalization=data["market_capitalization"],
            industry_type=data["industry_type"],
        )

    def _decode(self, html_page: StockInfoHtmlPage) -> dict:
        soup = html_page.get_as_soup()
        result: Dict[str, Union[str, bool, int, float, List[str]]] = {}

        stock_board_tag = "md_stockBoard"

        raw_dt = PageDecoder(tag1="span", class1="fsm").decode(bs=soup)
        dt = datetime.strptime(raw_dt, "(%m/%d)").replace(year=datetime.now().year)

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
                "dt": dt.strftime("%y-%m-%d"),
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
