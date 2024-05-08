from dataclasses import dataclass

import pandas as pd
from bs4 import BeautifulSoup
from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError
from kabutobashi.domain.values import DecodeHtmlPageStockIpo

from ..abc_block import BlockGlue
from .abc_extract_block import IExtractBlock, IExtractBlockInput, IExtractBlockOutput


@dataclass(frozen=True)
class ExtractStockIpoBlockInput(IExtractBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        params = block_glue.block_outputs["crawl_stock_ipo"].params
        return ExtractStockIpoBlockInput(series=None, params=params)

    def _validate(self):
        if self.params is not None:
            keys = self.params.keys()
            assert "year" in keys, "StockIpoExtractBlockInput must have 'year' params"
            assert "html_text" in keys, "StockIpoExtractBlockInput must have 'code' params"


@dataclass(frozen=True)
class ExtractStockIpoBlockOutput(IExtractBlockOutput):
    block_name: str = "extract_stock_ipo"

    def _validate(self):
        keys = self.params.keys()
        assert "ipo_list" in keys, "StockIpoExtractBlockOutput must have 'ipo_list' column"


@inject
@dataclass(frozen=True)
class ExtractStockIpoBlock(IExtractBlock):

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

    def _process(self) -> ExtractStockIpoBlockOutput:
        if not isinstance(self.block_input, ExtractStockIpoBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        html_text = params["html_text"]
        # to_df
        result = self._decode(html_text=html_text)
        df = pd.DataFrame(data=result["ipo_list"])
        return ExtractStockIpoBlockOutput.of(series=df, params=result)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IExtractBlockInput, to=ExtractStockIpoBlockInput)  # type: ignore[type-abstract]
