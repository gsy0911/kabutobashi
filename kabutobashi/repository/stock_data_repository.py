from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generator, Union

import pandas as pd

from kabutobashi.domain.entity import StockDataMultipleCode
from kabutobashi.utilities import get_past_n_days


class IStockDataMultipleCodeReader(metaclass=ABCMeta):
    @abstractmethod
    def _path(self) -> Generator[str, None, None]:
        raise NotImplementedError()

    def read(self) -> StockDataMultipleCode:
        return self._read()

    def _read(self) -> StockDataMultipleCode:
        df = pd.concat([pd.read_csv(p) for p in self._path()])
        return StockDataMultipleCode.of(df=df)


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
            stock_data_multiple_code.df.to_csv(p)


class StockDataRepository:
    @staticmethod
    def read_multiple_code(path_candidate: Union[str, list]) -> StockDataMultipleCode:
        return StockDataMultipleCodeBasicReader(path_candidate=path_candidate).read()

    @staticmethod
    def read_multiple_code_from_past_n_days(path_format: str, start_date: str, n: int) -> StockDataMultipleCode:
        return StockDataMultipleCodeTargetDateReader(path_format=path_format, start_date=start_date, n=n).read()

    @staticmethod
    def write_multiple_code(multiple_code: StockDataMultipleCode, path_candidate: str):
        return StockDataMultipleCodeBasicWriter(path_candidate=path_candidate).write(
            stock_data_multiple_code=multiple_code
        )
