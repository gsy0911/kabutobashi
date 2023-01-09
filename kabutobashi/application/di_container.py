from typing import Optional

from injector import Binder, Module


class StockCrawlDi(Module):
    """
    Model: DI Container (for crawl and decode)
    """

    def __init__(self, page_type: str, *, code: Optional[str] = None, year: Optional[str] = None):
        self.page_type = page_type
        self.code = code
        self.year = year

    def configure(self, binder: Binder) -> None:
        # repository/decoders
        from kabutobashi.domain.services import (
            IHtmlDecoder,
            StockInfoMinkabuTopHtmlDecoder,
            StockInfoMultipleDaysHtmlDecoder,
            StockIpoHtmlDecoder,
        )
        from kabutobashi.domain.values import IHtmlPageRepository
        from kabutobashi.infrastructure.repository import (
            StockInfoHtmlPageRepository,
            StockInfoMultipleDaysHtmlPageRepository,
            StockIpoHtmlPageRepository,
        )

        if self.page_type == "info":
            # repository-bind
            binder.bind(IHtmlPageRepository, StockInfoHtmlPageRepository(code=self.code))
            # decoder-bind
            binder.bind(IHtmlDecoder, StockInfoMinkabuTopHtmlDecoder)
        elif self.page_type == "ipo":
            # repository-bind
            binder.bind(IHtmlPageRepository, StockIpoHtmlPageRepository(year=self.year))
            # decoder-bind
            binder.bind(IHtmlDecoder, StockIpoHtmlDecoder)
        elif self.page_type == "info_multiple":
            # repository-bind
            binder.bind(IHtmlPageRepository, StockInfoMultipleDaysHtmlPageRepository(code=self.code))
            # decoder-bind
            binder.bind(IHtmlDecoder, StockInfoMultipleDaysHtmlDecoder)
