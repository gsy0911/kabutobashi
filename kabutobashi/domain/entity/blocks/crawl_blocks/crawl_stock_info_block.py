from dataclasses import dataclass

from kabutobashi.domain.errors import KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue
from ..decorator import block
from .abc_crawl_block import ICrawlBlockInput, ICrawlBlockOutput, from_url


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


@block(block_name="crawl_stock_info")
class CrawlStockInfoBlock:
    code: str

    def _process(self) -> dict:
        html_text = from_url(url=f"https://minkabu.jp/stock/{self.code}")
        return {"code": self.code, "html_text": html_text}

    def _validate_code(self, code: str):
        if code is None:
            raise ValueError()
