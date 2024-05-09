from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue, IBlockInput
from .abc_crawl_block import ICrawlBlock, ICrawlBlockInput, ICrawlBlockOutput


@dataclass(frozen=True)
class CrawlStockInfoMultipleDaysBlockInput(ICrawlBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        params = block_glue.params["crawl_stock_info_multiple_days"]
        return CrawlStockInfoMultipleDaysBlockInput(series=None, params=params)

    def _validate(self):
        if self.params is not None:
            keys = self.params.keys()
            assert "code" in keys, "StockInfoMultipleDaysCrawlBlockInput must have 'code' params"


@dataclass(frozen=True)
class CrawlStockInfoMultipleDaysBlockOutput(ICrawlBlockOutput):
    block_name: str = "crawl_stock_info_multiple_days"

    def _validate(self):
        keys = self.params.keys()
        assert "code" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'code' column"
        assert "main_html_text" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'main_html_text' column"
        assert "sub_html_text" in keys, "StockInfoMultipleDaysCrawlBlockOutput must have 'sub_html_text' column"


@inject
@dataclass(frozen=True)
class CrawlStockInfoMultipleDaysBlock(ICrawlBlock):

    def _process(self) -> CrawlStockInfoMultipleDaysBlockOutput:
        if not isinstance(self.block_input, CrawlStockInfoMultipleDaysBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        code = params["code"]
        main_html_text = self._from_url(url=f"https://minkabu.jp/stock/{code}/daily_bar")
        sub_html_text = self._from_url(url=f"https://minkabu.jp/stock/{code}/daily_valuation")
        return CrawlStockInfoMultipleDaysBlockOutput.of(
            series=None, params={"code": code, "main_html_text": main_html_text, "sub_html_text": sub_html_text}
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(ICrawlBlockInput, to=CrawlStockInfoMultipleDaysBlockInput)  # type: ignore[type-abstract]
