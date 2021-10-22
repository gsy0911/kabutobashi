from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Weeks52HighLow:
    """
    52週高値・底値
    """

    code: int
    brand_name: str
    close: int
    buy: str
    strong_buy: str
    sell: str
    strong_sell: str
    buy_or_sell: str
    volatility_up: float
    volatility_down: float
    volatility_ratio: float
    volatility_value: float

    @staticmethod
    def from_page_of(data: dict) -> "Weeks52HighLow":
        buy = data["buy"]
        strong_buy = data["strong_buy"]
        sell = data["sell"]
        strong_sell = data["strong_sell"]

        return Weeks52HighLow(
            code=int(data["code"]),
            brand_name=data["brand_name"],
            close=data["close"],
            buy=buy,
            strong_buy=strong_buy,
            sell=sell,
            strong_sell=strong_sell,
            buy_or_sell=f"{buy}{strong_buy}{sell}{strong_sell}",
            volatility_up=data["volatility_up"],
            volatility_down=data["volatility_down"],
            volatility_ratio=data["volatility_ratio"],
            volatility_value=data["volatility_value"],
        )

    def dumps(self) -> dict:
        return asdict(self)
