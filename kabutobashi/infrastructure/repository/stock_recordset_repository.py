from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Generator, List, Union

import pandas as pd

from kabutobashi.domain.values import IStockRecordsetRepository, StockRecordset
from kabutobashi.infrastructure.crawler import crawl_multiple

__all__ = ["IStockRecordsetStorageRepository", "StockRecordsetStorageBasicRepository", "StockRecordsetCrawler"]


class IStockRecordsetStorageRepository(IStockRecordsetRepository):
    def __init__(self, use_mp: bool, max_workers: int):
        self.use_mp = use_mp
        self.max_workers = max_workers

    @abstractmethod
    def _read_path_generator(self) -> Generator[str, None, None]:
        raise NotImplementedError()

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

    @abstractmethod
    def _write_path_generator(self) -> Generator[str, None, None]:
        raise NotImplementedError()

    def _stock_recordset_write(self, data: StockRecordset):
        df = data.to_df(minimum=False)
        for p in self._write_path_generator():
            df.to_csv(p, index=False)


class StockRecordsetStorageBasicRepository(IStockRecordsetStorageRepository):
    def __init__(self, path_candidate: Union[str, list], use_mp: bool = False, max_workers: int = 2):
        super().__init__(use_mp=use_mp, max_workers=max_workers)
        self.path_candidate = path_candidate

    def _read_path_generator(self) -> Generator[str, None, None]:
        if type(self.path_candidate) is str:
            yield self.path_candidate
        elif type(self.path_candidate) is list:
            for path in self.path_candidate:
                yield path
        else:
            raise ValueError()

    def _write_path_generator(self) -> Generator[str, None, None]:
        if type(self.path_candidate) is str:
            yield self.path_candidate
        elif type(self.path_candidate) is list:
            for path in self.path_candidate:
                yield path
        else:
            raise ValueError()


class StockRecordsetCrawler:
    def __init__(self, use_mp: bool = False, max_workers: int = 2):
        self.use_mp = use_mp
        self.max_workers = max_workers

    def get(self, code_list: list, dt: str) -> StockRecordset:
        # 日次の株データ取得
        stock_data: List[dict] = crawl_multiple(code_list=code_list, max_workers=self.max_workers, dt=dt)

        # データを整形してStockDataとして保存
        df = pd.DataFrame(stock_data)
        return StockRecordset.of(df=df)
