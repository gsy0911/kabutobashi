from typing import Optional

from injector import Binder, Module


class StockCrawlDi(Module):
    """
    Model: DI Container (for crawl and decode)
    """

    def __init__(self, page_type: str, *, code: Optional[str] = None):
        self.page_type = page_type
        self.code = code

    def configure(self, binder: Binder) -> None:
        # repository/decoders
        from kabutobashi.domain.services import IHtmlDecoder, StockInfoMinkabuTopHtmlDecoder
        from kabutobashi.domain.values import IHtmlPageRepository
        from kabutobashi.infrastructure.repository import StockInfoHtmlPageRepository

        # repository-bind
        binder.bind(IHtmlPageRepository, StockInfoHtmlPageRepository(code=self.code))
        # decoder-bind
        binder.bind(IHtmlDecoder, StockInfoMinkabuTopHtmlDecoder)
