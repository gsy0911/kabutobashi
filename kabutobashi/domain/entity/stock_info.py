from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class StockInfo:
    code: str
    market: str
    industry_type: str
    open: int
    high: int
    low: int
    close: int
    psr: float
    per: float
    pbr: float
    volume: int
    unit: int
    market_capitalization: str
    issued_shares: str
    dt: str

    def __post_init__(self):
        pass

    @staticmethod
    def from_page_of(data: dict) -> "StockInfo":
        label_split = data["stock_label"].split("  ")
        return StockInfo(
            code=label_split[0],
            market=label_split[1],
            industry_type=data["industry_type"],
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            unit=data["unit"],
            psr=data["psr"],
            per=data["per"],
            pbr=data["pbr"],
            volume=data["volume"],
            market_capitalization=data["market_capitalization"],
            issued_shares=data["issued_shares"],
            dt=data["date"],
        )

    def dumps(self) -> dict:
        return asdict(self)
