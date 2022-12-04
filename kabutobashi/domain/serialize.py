from abc import ABC, abstractmethod


class IDictSerialize(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_dict(data: dict):
        raise NotImplementedError()


class ICsvLineSerialize(ABC):
    @abstractmethod
    def to_line(self) -> str:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_line(data: str):
        raise NotImplementedError()
