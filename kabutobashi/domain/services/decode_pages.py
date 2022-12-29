import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from functools import reduce
from logging import getLogger
from typing import Dict, List, Optional, Union

import pandas as pd
from bs4 import BeautifulSoup

from kabutobashi.domain.entity import StockIpo
from kabutobashi.domain.values import (
    HtmlPage,
    StockInfoHtmlPage,
    StockInfoMultipleDaysMainHtmlPage,
    StockInfoMultipleDaysSubHtmlPage,
    StockIpoHtmlPage,
)

logger = getLogger(__name__)
__all__ = [
    "IHtmlDecoder",
    "PageDecoder",
    "StockInfoHtmlDecoder",
    "StockIpoHtmlDecoder",
    "StockInfoMultipleDaysHtmlDecoder",
]


@dataclass(frozen=True)
class PageDecoder:
    tag1: Optional[str] = None
    class1: Optional[str] = None
    id1: Optional[str] = None
    default: str = ""

    def _decode(self, value):
        class1 = {"class": self.class1}

        set_value = None
        # tag1から取得
        if self.tag1 is not None:
            if class1["class"] is not None:
                set_value = value.find(self.tag1, self.class1)
            else:
                set_value = value.find(self.tag1)

        if set_value is None:
            return self.default

        # 文字列を置換して保持
        return self.replace(set_value.get_text())

    def decode(self, bs: BeautifulSoup) -> Union[str, List[str]]:
        return self._decode(value=bs)

    @staticmethod
    def replace(input_text: str) -> str:
        target_list = [" ", "\t", "\n", "\r", "円"]

        def remove_of(_input: str, target: str):
            return _input.replace(target, "")

        result = reduce(remove_of, target_list, input_text)
        return result.replace("\xa0", " ")


@dataclass(frozen=True)  # type: ignore
class IHtmlDecoder(ABC):
    @abstractmethod
    def _decode(self, html_page: HtmlPage) -> dict:
        raise NotImplementedError()

    def decode(self, html_page: HtmlPage) -> dict:
        return self._decode(html_page=html_page)

    # @abstractmethod
    # def _decode_to_object_hook(self, data: dict):
    #     raise NotImplementedError()
    #
    # def decode_to_object(self, html_page: HtmlPage):
    #     data = self._decode(html_page=html_page)
    #     return self._decode_to_object_hook(data=data)


@dataclass(frozen=True)
class StockInfoHtmlDecoder(IHtmlDecoder):
    """
    TODO BrandとRecordとで役割を分割する

    Examples:
        >>> import kabutobashi as kb
        >>> # get single page
        >>> page_html = kb.StockInfoHtmlPageRepository(code="0001").read()
        >>> result = StockInfoHtmlDecoder().decode(page_html=page_html)
    """

    def _decode(self, html_page: StockInfoHtmlPage) -> dict:
        soup = html_page.get_as_soup()
        result: Dict[str, Union[str, bool, int, float, List[str]]] = {}

        stock_board_tag = "md_stockBoard"

        raw_dt = PageDecoder(tag1="span", class1="fsm").decode(bs=soup)
        pattern = r"\((?P<month>[0-9]+)/(?P<day>[0-9]+)\)|\((?P<hour>[0-9]+):(?P<minute>[0-9]+)\)"
        match_result = re.match(pattern, raw_dt)
        dt = datetime.now()
        if result:
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
                "is_delisting": False,
            }
        )

        # 上場廃止の確認
        open_value = result["open"]
        high_value = result["high"]
        low_value = result["low"]
        if open_value == "---" and high_value == "---" and low_value == "---":
            result.update({"is_delisting": True})
        return result


@dataclass(frozen=True)
class StockIpoHtmlDecoder(IHtmlDecoder):
    def _decode(self, html_page: StockIpoHtmlPage) -> dict:
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
            whole_result.append(StockIpo.from_dict(data=table_body_dict).to_dict())
        return {"ipo_list": whole_result}


@dataclass(frozen=True)
class StockInfoMultipleDaysHtmlDecoder(IHtmlDecoder):
    """

    Examples:
        >>> import kabutobashi as kb
        >>> main_html_page = kb.StockInfoMultipleDaysMainHtmlPageRepository(code=1375).read()
        >>> sub_html_page = kb.StockInfoMultipleDaysSubHtmlPageRepository(code=1375).read()
        >>> data = kb.StockInfoMultipleDaysHtmlDecoder(main_html_page, sub_html_page).decode()
        >>> df = pd.DataFrame(data)
        >>> records = kb.StockRecordset.of(df)
    """

    main_html_page: StockInfoMultipleDaysMainHtmlPage
    sub_html_page: StockInfoMultipleDaysSubHtmlPage

    def _decode(self, html_page: StockIpoHtmlPage) -> dict:
        result_1 = []
        result_2 = []
        main_soup = self.main_html_page.get_as_soup()
        sub_soup = self.sub_html_page.get_as_soup()
        stock_recordset_tag = "md_card md_box"

        # ページの情報を取得
        stock_recordset = main_soup.find("div", {"class": stock_recordset_tag})
        mapping = {0: "dt", 1: "open", 2: "high", 3: "low", 4: "close", 5: "調整後終値", 6: "volume"}
        for tr in stock_recordset.find_all("tr"):
            tmp = {}
            for idx, td in enumerate(tr.find_all("td")):
                tmp.update({mapping[idx]: td.get_text()})
            result_1.append(tmp)

        # そのほかの情報
        stock_board = sub_soup.find("div", {"class": "md_card md_box mzp"})
        mapping2 = {0: "dt", 1: "psr", 2: "per", 3: "pbr", 4: "配当利回り(%)", 5: "close", 6: "調整後終値", 7: "volume"}
        for tr in stock_board.find_all("tr"):
            tmp = {}
            for idx, td in enumerate(tr.find_all("td")):
                tmp.update({mapping2[idx]: td.get_text()})
            result_2.append(tmp)

        df1 = pd.DataFrame(result_1).dropna()
        df2 = pd.DataFrame(result_2).dropna()

        df1 = df1[["dt", "open", "high", "low", "close"]]
        df2 = df2[["dt", "psr", "per", "pbr", "volume"]]

        df = pd.merge(df1, df2, on="dt")
        df["code"] = self.main_html_page.code
        return df.to_dict(orient="records")
