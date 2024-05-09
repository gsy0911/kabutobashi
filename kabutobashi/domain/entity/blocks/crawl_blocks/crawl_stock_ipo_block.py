from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue, IBlockInput
from .abc_crawl_block import ICrawlBlock, ICrawlBlockInput, ICrawlBlockOutput


@dataclass(frozen=True)
class CrawlStockIpoBlockInput(ICrawlBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        params = block_glue.params["crawl_stock_ipo"]
        return CrawlStockIpoBlockInput(series=None, params=params)

    def _validate(self):
        if self.params is not None:
            keys = self.params.keys()
            assert "year" in keys, "StockIpoCrawlBlockInput must have 'year' params"


@dataclass(frozen=True)
class CrawlStockIpoBlockOutput(ICrawlBlockOutput):
    block_name: str = "crawl_stock_ipo"

    def _validate(self):
        keys = self.params.keys()
        assert "year" in keys, "StockIpoCrawlBlockOutput must have 'year' column"
        assert "html_text" in keys, "StockIpoCrawlBlockOutput must have 'html_text' column"


@inject
@dataclass(frozen=True)
class CrawlStockIpoBlock(ICrawlBlock):

    def _process(self) -> CrawlStockIpoBlockOutput:
        if not isinstance(self.block_input, CrawlStockIpoBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        year = params["year"]
        html_text = self._from_url(url=f"https://96ut.com/ipo/list.php?year={year}")
        return CrawlStockIpoBlockOutput.of(series=None, params={"year": year, "html_text": html_text})

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(ICrawlBlockInput, to=CrawlStockIpoBlockInput)  # type: ignore[type-abstract]
