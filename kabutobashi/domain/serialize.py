from abc import ABC, abstractmethod


class IDictSerialize(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_dict(data: dict):
        raise NotImplementedError()
