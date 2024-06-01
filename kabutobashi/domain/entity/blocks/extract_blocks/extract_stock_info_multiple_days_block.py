from typing import Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup

from ..decorator import block


@block(block_name="extract_stock_info_multiple_days", pre_condition_block_name="crawl_stock_info_multiple_days")
class ExtractStockInfoMultipleDaysBlock:
    main_html_text: str
    sub_html_text: str
    code: str

    def _decode(self, code: str, main_html_text: str, sub_html_text: str) -> dict:
        result_1 = []
        result_2 = []
        main_soup = BeautifulSoup(main_html_text, features="lxml")
        sub_soup = BeautifulSoup(sub_html_text, features="lxml")
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
        df["code"] = code
        return {"info_list": df.to_dict(orient="records")}

    def _process(self) -> Tuple[pd.DataFrame, dict]:
        result = self._decode(code=self.code, main_html_text=self.main_html_text, sub_html_text=self.sub_html_text)
        # to_df
        df = pd.DataFrame(data=result["info_list"])
        df.index = df["dt"]
        return df, result

    def _validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]):
        keys = series.keys()
        assert "info_list" in keys, "StockInfoMultipleDaysExtractBlockOutput must have 'info_list' column"
