import functools
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from typing import Generator, List, Union

import pandas as pd

from kabutobashi.domain.errors import KabutobashiPageError
from kabutobashi.domain.services import StockInfoHtmlDecoder
from kabutobashi.domain.values import IStockRecordsetRepository, StockRecordset
from kabutobashi.infrastructure.repository import StockInfoHtmlPageRepository

logger = getLogger(__name__)


__all__ = ["StockRecordsetStorageBasicRepository", "StockRecordsetCrawler"]


class StockRecordsetStorageBasicRepository(IStockRecordsetRepository):
    def __init__(self, path_candidate: Union[str, list], use_mp: bool = False, max_workers: int = 2):
        self.path_candidate = path_candidate
        self.use_mp = use_mp
        self.max_workers = max_workers

    def _read_path_generator(self) -> Generator[str, None, None]:
        if type(self.path_candidate) is str:
            yield self.path_candidate
        elif type(self.path_candidate) is list:
            for path in self.path_candidate:
                yield path
        else:
            raise ValueError()

    def _stock_recordset_read(self) -> StockRecordset:
        df_list = []
        if self.use_mp:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                map_gen = executor.map(pd.read_csv, self._read_path_generator())
                for response in map_gen:
                    df_list.append(response)
        else:
            df_list = [pd.read_csv(p) for p in self._read_path_generator()]

        df = pd.concat(df_list)
        return StockRecordset.of(df=df)

    def _write_path_generator(self) -> Generator[str, None, None]:
        if type(self.path_candidate) is str:
            yield self.path_candidate
        elif type(self.path_candidate) is list:
            for path in self.path_candidate:
                yield path
        else:
            raise ValueError()

    def _stock_recordset_write(self, data: StockRecordset):
        df = data.to_df(minimum=False)
        for p in self._write_path_generator():
            df.to_csv(p, index=False)


class StockRecordsetCrawler(IStockRecordsetRepository):
    def __init__(self, code_list: list, use_mp: bool = False, max_workers: int = 2):
        self.code_list = code_list
        self.use_mp = use_mp
        self.max_workers = max_workers

    def _stock_recordset_read(self) -> StockRecordset:

        # 日次の株データ取得
        stock_data: List[dict] = []
        if self.use_mp:
            stock_data.extend(self.crawl_multiple(code_list=self.code_list, max_workers=self.max_workers))
        else:
            stock_data.extend([self.crawl_single(code=code) for code in self.code_list])

        # データを整形してStockDataとして保存
        df = pd.DataFrame(stock_data)
        return StockRecordset.of(df=df)

    @staticmethod
    def crawl_single(code: Union[int, str]) -> dict:
        try:
            stock_page_html = StockInfoHtmlPageRepository(code=code).read()
            result = StockInfoHtmlDecoder().decode(html_page=stock_page_html)
            return result
        except KabutobashiPageError:
            return {}
        except AttributeError:
            logger.exception(f"error occurred at: {code}")
            return {}
        except Exception:
            logger.exception(f"error occurred at: {code}")
            return {}

    @staticmethod
    def crawl_multiple(code_list: List[Union[int, str]], max_workers: int = 2) -> List[dict]:
        partial_crawl_single = functools.partial(StockRecordsetCrawler.crawl_single)
        response_list = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            map_gen = executor.map(partial_crawl_single, code_list)
            for response in map_gen:
                response_list.append(response)
        return response_list

    def _stock_recordset_write(self, data: StockRecordset):
        raise NotImplementedError()
