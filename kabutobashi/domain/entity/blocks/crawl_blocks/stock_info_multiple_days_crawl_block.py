from dataclasses import dataclass

from injector import Binder, inject

from ..abc_block import BlockGlue
from .abc_crawl_block import ICrawlBlock, ICrawlBlockInput, ICrawlBlockOutput


@dataclass(frozen=True)
class StockInfoMultipleDaysCrawlBlockInput(ICrawlBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        params = block_glue.block_outputs["stock_info_multiple_days_crawl"].params
        return StockInfoMultipleDaysCrawlBlockInput(series=None, params=params)

    def _validate(self):
        keys = self.params.keys()
        assert "code" in keys, "StockInfoMultipleDaysCrawlBlockInput must have 'code' params"


@dataclass(frozen=True)
class StockInfoMultipleDaysCrawlBlockOutput(ICrawlBlockOutput):
    block_name: str = "stock_info_multiple_days_crawl"

    def _validate(self):
        keys = self.params.keys()
        assert "code" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'code' column"
        assert "main_html_text" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'main_html_text' column"
        assert "sub_html_text" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'sub_html_text' column"


@inject
@dataclass(frozen=True)
class StockInfoMultipleDaysCrawlBlock(ICrawlBlock):

    def _process(self, block_input: StockInfoMultipleDaysCrawlBlockInput) -> StockInfoMultipleDaysCrawlBlockOutput:
        params = block_input.params
        code = params["code"]

        main_html_text = self._from_url(url=f"https://minkabu.jp/stock/{code}/daily_bar")
        sub_html_text = self._from_url(url=f"https://minkabu.jp/stock/{code}/daily_valuation")
        return StockInfoMultipleDaysCrawlBlockOutput.of(
            series=None, params={"code": code, "main_html_text": main_html_text, "sub_html_text": sub_html_text}
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(ICrawlBlockInput, to=StockInfoMultipleDaysCrawlBlockInput)
