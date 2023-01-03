from dataclasses import dataclass

from injector import Injector, inject

from kabutobashi.domain.services import IHtmlDecoder
from kabutobashi.domain.values import IHtmlPageRepository

from .di_container import StockCrawlDi


@inject
@dataclass
class DataCrawlController:
    html_page_repository: IHtmlPageRepository
    html_decoder: IHtmlDecoder

    def run(self):
        # code: str
        page_html = self.html_page_repository.read()
        return self.html_decoder.decode_to_object(html_page=page_html)


def crawl(code: str):
    di = Injector([StockCrawlDi(page_type="info", code=code)])
    data_crawler = di.get(DataCrawlController)
    return data_crawler.run()
