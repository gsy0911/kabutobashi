from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
from logging import getLogger
from typing import List, Optional, Union

from bs4 import BeautifulSoup

from kabutobashi.domain.values import RawHtmlPage

logger = getLogger(__name__)
__all__ = ["IHtmlDecoder", "PageDecoder"]


@dataclass(frozen=True)
class PageDecoder:
    tag1: Optional[str] = None
    class1: Optional[str] = None
    id1: Optional[str] = None
    default: str = ""

    def _decode(self, value):
        class1 = {"class": self.class1}

        set_value = None
        # tag1から取得
        if self.tag1 is not None:
            if class1["class"] is not None:
                set_value = value.find(self.tag1, self.class1)
            else:
                set_value = value.find(self.tag1)

        if set_value is None:
            return self.default

        # 文字列を置換して保持
        return self.replace(set_value.get_text())

    def decode(self, bs: BeautifulSoup) -> Union[str, List[str]]:
        return self._decode(value=bs)

    @staticmethod
    def replace(input_text: str) -> str:
        target_list = [" ", "\t", "\n", "\r", "円"]

        def remove_of(_input: str, target: str):
            return _input.replace(target, "")

        result = reduce(remove_of, target_list, input_text)
        return result.replace("\xa0", " ")


@dataclass(frozen=True)  # type: ignore
class IHtmlDecoder(ABC):
    """
    Model: Service(Interface)
    JP: HTML変換サービス
    """

    @abstractmethod
    def _decode(self, html_page: RawHtmlPage) -> dict:
        raise NotImplementedError()  # pragma: no cover

    def decode_to_dict(self, html_page: RawHtmlPage) -> dict:
        return self._decode(html_page=html_page)

    @abstractmethod
    def _decode_to_object_hook(self, data: dict) -> object:
        raise NotImplementedError()  # pragma: no cover

    def decode_to_object(self, html_page: RawHtmlPage) -> object:
        data = self._decode(html_page=html_page)
        return self._decode_to_object_hook(data=data)
