from dataclasses import dataclass
from functools import reduce
from logging import getLogger
from typing import Dict, List, Optional, Union

import pandas as pd
from bs4 import BeautifulSoup

from kabutobashi.domain.entity import StockIpo, Weeks52HighLow
from kabutobashi.domain.values import (
    StockInfoHtmlPage,
    StockInfoMultipleDaysMainHtmlPage,
    StockInfoMultipleDaysSubHtmlPage,
    StockIpoHtmlPage,
    StockWeeks52HighLowHtmlPage,
)

logger = getLogger(__name__)


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


@dataclass(frozen=True)
class StockInfoHtmlDecoder:
    """

    Examples:
        >>> from kabutobashi import StockInfoHtmlPage
        >>> # get single page
        >>> page_html = StockInfoHtmlPage.of(code="0001", dt="2022-07-22")
        >>> result = StockInfoHtmlDecoder(page_html=page_html).decode()
    """

    html_page: StockInfoHtmlPage

    def decode(self) -> dict:
        soup = self.html_page.get_as_soup()
        result: Dict[str, Union[str, bool, int, float, List[str]]] = {}

        stock_board_tag = "md_stockBoard"

        # ページ上部の情報を取得
        stock_board = soup.find("div", {"class": stock_board_tag})
        result.update(
            {
                "stock_label": PageDecoder(tag1="div", class1="stock_label").decode(bs=stock_board),
                "name": PageDecoder(tag1="p", class1="md_stockBoard_stockName").decode(bs=stock_board),
                "close": PageDecoder(tag1="div", class1="stock_price").decode(bs=stock_board),
                # "date": PageDecoder(tag1="h2", class1="stock_label fsl").decode(bs=stock_board),
            }
        )

        # ページ中央の情報を取得
        stock_detail = soup.find("div", {"id": "main"})
        info = {}
        for li in stock_detail.find_all("tr", {"class": "ly_vamd"}):
            info[li.find("th").get_text()] = li.find("td").get_text()
        stock_label = str(result.get("stock_label", ""))
        result.update(
            {
                "dt": self.html_page.dt,
                "code": str(self.html_page.code),
                "industry_type": PageDecoder(tag1="div", class1="ly_content_wrapper size_ss").decode(bs=stock_detail),
                "market": stock_label.replace(" ", "").replace(str(self.html_page.code), ""),
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
class StockIpoHtmlDecoder:

    html_page: StockIpoHtmlPage

    def decode(self) -> dict:
        soup = self.html_page.get_as_soup()
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
            whole_result.append(StockIpo.loads(data=table_body_dict).dumps())
        return {"ipo_list": whole_result}


@dataclass(frozen=True)
class Weeks52HighLowHtmlDecoder:
    html_page: StockWeeks52HighLowHtmlPage

    def decode(self) -> dict:
        soup = self.html_page.get_as_soup()

        content = soup.find("body").find("tbody")
        table = content.find_all("tr")
        whole_result = []
        for t in table:
            buy_or_sell = ""

            for td in t.find_all("td"):
                if td.text in ["買い", "強い買い", "売り", "強い売り"]:
                    buy_or_sell = td.text
            data = {
                "code": PageDecoder(tag1="a").decode(bs=t),
                "brand_name": PageDecoder(tag1="span").decode(bs=t),
                "buy_or_sell": buy_or_sell,
                "dt": self.html_page.dt,
            }
            whole_result.append(Weeks52HighLow.from_page_of(data=data).dumps())

        return {"weeks_52_high_low": whole_result}


@dataclass(frozen=True)
class StockInfoMultipleDaysHtmlDecoder:
    """

    Examples:
        >>> import kabutobashi as kb
        >>> main_html_page = kb.StockInfoMultipleDaysMainHtmlPage.of(1375)
        >>> sub_html_page = kb.StockInfoMultipleDaysSubHtmlPage.of(1375)
        >>> data = kb.StockInfoMultipleDaysHtmlDecoder(main_html_page, sub_html_page).decode()
        >>> df = pd.DataFrame(data)
        >>> records = kb.StockRecordset.of(df)
    """

    main_html_page: StockInfoMultipleDaysMainHtmlPage
    sub_html_page: StockInfoMultipleDaysSubHtmlPage

    def decode(self) -> dict:
        result_1 = []
        result_2 = []
        main_soup = self.main_html_page.get_as_soup()
        sub_soup = self.sub_html_page.get_as_soup()
        stock_recordset_tag = "md_card md_box"

        # ページの情報を取得
        stock_recordset = main_soup.find("div", {"class": stock_recordset_tag})
        # code,market,name,industry_type,open,high,low,close,psr,per,pbr,volume,unit,market_capitalization,issued_shares,dt,crawl_datetime
        mapping = {0: "dt", 1: "open", 2: "high", 3: "low", 4: "close", 5: "調整後終値", 6: "volume"}
        for tr in stock_recordset.find_all("tr"):
            tmp = {}
            for idx, td in enumerate(tr.find_all("td")):
                tmp.update({mapping[idx]: td.get_text()})
            result_1.append(tmp)

        # そのほかの情報
        # soup = BeautifulSoup(get_url_text(url=valuation_url.format(code=code)), features="lxml")
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
