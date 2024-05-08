from dataclasses import dataclass

from bs4 import BeautifulSoup
from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError
from kabutobashi.domain.values import DecodeHtmlPageStockIpo

from ..abc_block import BlockGlue, IBlockInput
from .abc_extract_block import IExtractBlock, IExtractBlockInput, IExtractBlockOutput


@dataclass(frozen=True)
class StockIpoExtractBlockInput(IExtractBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        params = block_glue.block_outputs["stock_info_crawl"].params
        return StockIpoExtractBlockInput(series=None, params=params)

    def _validate(self):
        if self.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        keys = self.params.keys()
        assert "year" in keys, "StockIpoExtractBlockInput must have 'year' params"
        assert "html_text" in keys, "StockIpoExtractBlockInput must have 'code' params"


@dataclass(frozen=True)
class StockIpoExtractBlockOutput(IExtractBlockOutput):
    block_name: str = "stock_info_crawl"

    def _validate(self):
        keys = self.params.keys()
        assert "ipo_list" in keys, "StockIpoExtractBlockOutput must have 'ipo_list' column"


@inject
@dataclass(frozen=True)
class StockIpoExtractBlock(IExtractBlock):

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

    def _process(self) -> StockIpoExtractBlockOutput:
        if not isinstance(self.block_input, StockIpoExtractBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        html_text = params["html_text"]
        result = self._decode(html_text=html_text)
        return StockIpoExtractBlockOutput.of(series=None, params=result)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=StockIpoExtractBlockInput)  # type: ignore[type-abstract]
