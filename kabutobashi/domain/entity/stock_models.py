from typing import Optional

from pydantic import BaseModel, Field

from kabutobashi.domain.serialize import IDictSerialize

from .util import _convert_float

__all__ = ["StockIpo"]


class StockIpo(BaseModel, IDictSerialize):
    """
    まだ取り込んでない値など

    '想定(仮条件)': '1,920(1,900-1,920)',
    '吸収金額': '75.6億',
    '(騰落率)損益': '(+1.1%)+2,100円00001',

    """

    id: int = Field(description="id")
    code: str = Field(description="銘柄コード")
    manager: str = Field(description="主幹")
    stock_listing_at: str = Field(description="上場日")
    public_offering: float = Field(description="公募")
    evaluation: str = Field(description="評価")
    initial_price: float = Field(description="初値")

    def __init__(
        self,
        id: Optional[int],
        code: str,
        manager: str,
        stock_listing_at: str,
        public_offering: float,
        evaluation: str,
        initial_price: float,
    ):
        if id is None:
            id = 0
        super().__init__(
            id=id,
            code=code,
            manager=manager,
            stock_listing_at=stock_listing_at,
            public_offering=public_offering,
            evaluation=evaluation,
            initial_price=initial_price,
        )

    @staticmethod
    def from_dict(data: dict) -> "StockIpo":
        return StockIpo(
            id=data.get("id"),
            code=data["code"],
            manager=data["主幹"],
            stock_listing_at=data["上場"],
            public_offering=_convert_float(data["公募"]),
            evaluation=data["評価"],
            initial_price=_convert_float(data["初値"]),
        )

    def to_dict(self) -> dict:
        return self.dict()

    class Config:
        orm_mode = True
