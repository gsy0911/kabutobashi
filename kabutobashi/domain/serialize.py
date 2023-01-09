from abc import ABC, abstractmethod

import pandas as pd


class IDictSerialize(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError()  # pragma: no cover

    @staticmethod
    @abstractmethod
    def from_dict(data: dict):
        raise NotImplementedError()  # pragma: no cover


class IDfSerialize(ABC):
    @abstractmethod
    def to_df(self) -> pd.DataFrame:
        raise NotImplementedError()  # pragma: no cover

    @staticmethod
    @abstractmethod
    def from_df(data: pd.DataFrame):
        raise NotImplementedError()  # pragma: no cover
