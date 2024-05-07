from dataclasses import dataclass

from injector import Binder, inject

from ..abc_block import BlockGlue
from .abc_crawl_block import ICrawlBlock, ICrawlBlockInput, ICrawlBlockOutput


@dataclass(frozen=True)
class StockIpoCrawlBlockInput(ICrawlBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        params = block_glue.block_outputs["stock_ipo_crawl"].params
        return StockIpoCrawlBlockInput(series=None, params=params)

    def _validate(self):
        keys = self.params.keys()
        assert "year" in keys, "StockIpoCrawlBlockInput must have 'year' params"


@dataclass(frozen=True)
class StockIpoCrawlBlockOutput(ICrawlBlockOutput):
    block_name: str = "stock_ipo_crawl"

    def _validate(self):
        keys = self.params.keys()
        assert "year" in keys, "StockIpoCrawlBlockOutput must have 'year' column"
        assert "html_text" in keys, "StockIpoCrawlBlockOutput must have 'html_text' column"


@inject
@dataclass(frozen=True)
class StockIpoCrawlBlock(ICrawlBlock):

    def _process(self, block_input: StockIpoCrawlBlockInput) -> StockIpoCrawlBlockOutput:
        params = block_input.params
        year = params["year"]
        html_text = self._from_url(url=f"https://96ut.com/ipo/list.php?year={year}")
        return StockIpoCrawlBlockOutput.of(series=None, params={"year": year, "html_text": html_text})

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(ICrawlBlockInput, to=StockIpoCrawlBlockInput)
