from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue, IBlockInput
from .abc_crawl_block import ICrawlBlock, ICrawlBlockInput, ICrawlBlockOutput


@dataclass(frozen=True)
class CrawlStockInfoBlockInput(ICrawlBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        params = block_glue.params["crawl_stock_info"]
        return CrawlStockInfoBlockInput(series=None, params={"code": params["code"]})

    def _validate(self):
        if self.params is not None:
            keys = self.params.keys()
            assert "code" in keys, "CrawlStockInfoBlockInput must have 'code' params"


@dataclass(frozen=True)
class CrawlStockInfoBlockOutput(ICrawlBlockOutput):
    block_name: str = "crawl_stock_info"

    def _validate(self):
        keys = self.params.keys()
        assert "code" in keys, "CrawlStockInfoBlockOutput must have 'code' column"
        assert "html_text" in keys, "CrawlStockInfoBlockOutput must have 'html_text' column"


@inject
@dataclass(frozen=True)
class CrawlStockInfoBlock(ICrawlBlock):

    def _process(self) -> CrawlStockInfoBlockOutput:
        if not isinstance(self.block_input, CrawlStockInfoBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        code = params["code"]
        html_text = self._from_url(url=f"https://minkabu.jp/stock/{code}")
        return CrawlStockInfoBlockOutput.of(series=None, params={"code": code, "html_text": html_text})

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(ICrawlBlockInput, to=CrawlStockInfoBlockInput)  # type: ignore[type-abstract]
