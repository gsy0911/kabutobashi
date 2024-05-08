from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue, IBlockInput
from .abc_crawl_block import ICrawlBlock, ICrawlBlockInput, ICrawlBlockOutput


@dataclass(frozen=True)
class StockInfoCrawlBlockInput(ICrawlBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        params = block_glue.block_outputs["stock_info_crawl"].params
        return StockInfoCrawlBlockInput(series=None, params=params)

    def _validate(self):
        keys = self.params.keys()
        assert "code" in keys, "StockInfoCrawlBlockInput must have 'code' params"


@dataclass(frozen=True)
class StockInfoCrawlBlockOutput(ICrawlBlockOutput):
    block_name: str = "stock_info_crawl"

    def _validate(self):
        keys = self.params.keys()
        assert "code" in keys, "StockInfoCrawlBlockOutput must have 'code' column"
        assert "html_text" in keys, "StockInfoCrawlBlockOutput must have 'html_text' column"


@inject
@dataclass(frozen=True)
class StockInfoCrawlBlock(ICrawlBlock):

    def _process(self, block_input: IBlockInput) -> StockInfoCrawlBlockOutput:
        if not isinstance(block_input, StockInfoCrawlBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        params = block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        code = params["code"]
        html_text = self._from_url(url=f"https://minkabu.jp/stock/{code}")
        return StockInfoCrawlBlockOutput.of(series=None, params={"code": code, "html_text": html_text})

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(ICrawlBlockInput, to=StockInfoCrawlBlockInput)
