from dataclasses import dataclass
from typing import Union
from .page import Page


@dataclass(frozen=True)
class StockCodePage(Page):
    base_url: str = "https://minkabu.jp/stock/{code}"

    def url(self) -> str:
        pass

    def get(self) -> dict:
        pass
