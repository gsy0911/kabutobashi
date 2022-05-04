from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Generator, Union

import pandas as pd

from kabutobashi.domain.entity import StockDataMultipleCode
from kabutobashi.domain.page import StockInfoPage
from kabutobashi.utilities import get_past_n_days

__all__ = ["StockDataMultipleCodeReader", "StockDataMultipleCodeWriter", "StockDataMultipleCodeCrawler"]


@dataclass(frozen=True)  # type: ignore
class IStockDataMultipleCodeReader(metaclass=ABCMeta):
    use_mp: bool
    max_workers: int

    @abstractmethod
    def _path(self) -> Generator[str, None, None]:
        raise NotImplementedError()

    def read(self) -> StockDataMultipleCode:
        return self._read()

    def _read(self) -> StockDataMultipleCode:
        df_list = []
        if self.use_mp:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                map_gen = executor.map(pd.read_csv, self._path())
                for response in map_gen:
                    df_list.append(response)
        else:
            df_list = [pd.read_csv(p) for p in self._path()]

        return StockDataMultipleCode.of(df=pd.concat(df_list))


@dataclass(frozen=True)
class StockDataMultipleCodeBasicReader(IStockDataMultipleCodeReader):
    path_candidate: Union[str, list]

    def _path(self) -> Generator[str, None, None]:
        if type(self.path_candidate) is str:
            yield self.path_candidate
        elif type(self.path_candidate) is list:
            for path in self.path_candidate:
                yield path
        else:
            raise ValueError()


@dataclass(frozen=True)
class StockDataMultipleCodeTargetDateReader(IStockDataMultipleCodeReader):
    path_format: str
    start_date: str
    n: int

    def _path(self) -> Generator[str, None, None]:
        date_list = get_past_n_days(current_date=self.start_date, n=self.n)
        path_list = [self.path_format.format(dt=dt) for dt in date_list]

        for path in path_list:
            yield path


class IStockDataMultipleCodeWriter(metaclass=ABCMeta):
    @abstractmethod
    def _path(self) -> Generator[str, None, None]:
        raise NotImplementedError()

    def write(self, stock_data_multiple_code: StockDataMultipleCode):
        return self._write(stock_data_multiple_code=stock_data_multiple_code)

    @abstractmethod
    def _write(self, stock_data_multiple_code: StockDataMultipleCode):
        raise NotImplementedError()


@dataclass(frozen=True)
class StockDataMultipleCodeBasicWriter(IStockDataMultipleCodeWriter):
    path_candidate: Union[str, list]

    def _path(self) -> Generator[str, None, None]:
        if type(self.path_candidate) is str:
            yield self.path_candidate
        elif type(self.path_candidate) is list:
            for path in self.path_candidate:
                yield path
        else:
            raise ValueError()

    def _write(self, stock_data_multiple_code: StockDataMultipleCode):
        # zip()をyieldでも利用できる？
        for p in self._path():
            stock_data_multiple_code.df.to_csv(p, index=False)


@dataclass
class StockDataMultipleCodeReader:
    use_mp: bool = False
    max_workers: int = 2

    def csv(self, path_candidate: Union[str, list]) -> StockDataMultipleCode:
        return StockDataMultipleCodeBasicReader(
            use_mp=self.use_mp, max_workers=self.max_workers, path_candidate=path_candidate
        ).read()

    def csv_from_past_n_days(self, path_format: str, start_date: str, n: int) -> StockDataMultipleCode:
        return StockDataMultipleCodeTargetDateReader(
            use_mp=self.use_mp, max_workers=self.max_workers, path_format=path_format, start_date=start_date, n=n
        ).read()


@dataclass
class StockDataMultipleCodeWriter:
    multiple_code: StockDataMultipleCode

    def csv(self, path_candidate: str):
        return StockDataMultipleCodeBasicWriter(path_candidate=path_candidate).write(
            stock_data_multiple_code=self.multiple_code
        )


@dataclass
class StockDataMultipleCodeCrawler:
    use_mp: bool = False
    max_workers: int = 2

    def get(self, code_list: list, dt: str):
        # 日次の株データ取得
        stock_data: list = StockInfoPage.crawl_multiple(code_list=code_list, max_workers=self.max_workers)

        # データを整形してStockDataとして保存
        df = pd.DataFrame(stock_data)
        df["dt"] = dt
        return StockDataMultipleCode.of(df=df)
