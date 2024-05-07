from dataclasses import dataclass

import pandas as pd
from bs4 import BeautifulSoup
from injector import Binder, inject

from ..abc_block import BlockGlue
from .abc_extract_block import IExtractBlock, IExtractBlockInput, IExtractBlockOutput


@dataclass(frozen=True)
class StockInfoMultipleDaysExtractBlockInput(IExtractBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        params = block_glue.block_outputs["stock_info_crawl"].params
        return StockInfoMultipleDaysExtractBlockInput(series=None, params=params)

    def _validate(self):
        keys = self.params.keys()
        assert "code" in keys, "StockInfoMultipleDaysExtractBlockInput must have 'code' params"
        assert "main_html_text" in keys, "StockInfoMultipleDaysExtractBlockInput must have 'main_html_text' params"
        assert "sub_html_text" in keys, "StockInfoMultipleDaysExtractBlockInput must have 'sub_html_text' params"


@dataclass(frozen=True)
class StockInfoMultipleDaysExtractBlockOutput(IExtractBlockOutput):
    block_name: str = "stock_info_crawl"

    def _validate(self):
        keys = self.params.keys()
        assert "info_list" in keys, "StockInfoMultipleDaysExtractBlockOutput must have 'info_list' column"


@inject
@dataclass(frozen=True)
class StockInfoMultipleDaysExtractBlock(IExtractBlock):

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

    def _process(self, block_input: StockInfoMultipleDaysExtractBlockInput) -> StockInfoMultipleDaysExtractBlockOutput:
        params = block_input.params
        main_html_text = params["main_html_text"]
        sub_html_text = params["sub_html_text"]
        code = params["code"]
        result = self._decode(code=code, main_html_text=main_html_text, sub_html_text=sub_html_text)
        return StockInfoMultipleDaysExtractBlockOutput.of(series=None, params=result)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IExtractBlockInput, to=StockInfoMultipleDaysExtractBlockInput)
