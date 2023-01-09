from dataclasses import dataclass

from injector import Injector, inject

from kabutobashi.domain.services import IHtmlDecoder, StockConverter
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


def crawl_info(code: str):
    di = Injector([StockCrawlDi(page_type="info", code=code)])
    data_crawler = di.get(DataCrawlController)
    info_object = data_crawler.run()
    return StockConverter().convert(value_object=info_object)


def crawl_info_multiple(code: str):
    di = Injector([StockCrawlDi(page_type="info_multiple", code=code)])
    data_crawler = di.get(DataCrawlController)
    info_object = data_crawler.run()
    return StockConverter().convert(value_object=info_object)


def crawl_ipo(year: str):
    di = Injector([StockCrawlDi(page_type="ipo", year=year)])
    data_crawler = di.get(DataCrawlController)
    ipo_list_object = data_crawler.run()
    return [StockConverter().convert(value_object=v) for v in ipo_list_object]
