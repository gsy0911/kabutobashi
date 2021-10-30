from dataclasses import asdict, dataclass

from cerberus import Validator

from kabutobashi.errors import KabutobashiEntityError


@dataclass(frozen=True)
class StockInfo:
    """
    Args:
        code: 銘柄コード
        market: 市場
        industry_type: 業種
        open: 円
        high: 円
        low: 円
        close: 円
    """

    code: str
    market: str
    name: str
    industry_type: str
    open: float
    high: float
    low: float
    close: float
    psr: float
    per: float
    pbr: float
    volume: int
    unit: int
    market_capitalization: str
    issued_shares: str
    dt: str
    _SCHEMA = {
        "code": {"type": "string"},
        "market": {"type": "string"},
        "industry_type": {"type": "string"},
        "name": {"type": "string"},
        "open": {"type": "float"},
        "high": {"type": "float"},
        "low": {"type": "float"},
        "close": {"type": "float"},
        "psr": {"type": "float"},
        "per": {"type": "float"},
        "pbr": {"type": "float"},
        "volume": {"type": "integer"},
        "unit": {"type": "integer"},
        "market_capitalization": {"type": "string"},
        "issued_shares": {"type": "string"},
        "dt": {"type": "string"},
    }

    def __post_init__(self):
        validator = Validator(self._SCHEMA)
        if not validator.validate(self.dumps()):
            raise KabutobashiEntityError(validator)

    @staticmethod
    def schema() -> list:
        return list(StockInfo._SCHEMA.keys())

    @staticmethod
    def from_page_of(data: dict) -> "StockInfo":
        label_split = data["stock_label"].split("  ")
        return StockInfo(
            code=label_split[0],
            market=label_split[1],
            name=data["name"],
            industry_type=data["industry_type"],
            open=float(StockInfo._convert(data["open"])),
            high=float(StockInfo._convert(data["high"])),
            low=float(StockInfo._convert(data["low"])),
            close=float(StockInfo._convert(data["close"])),
            unit=int(StockInfo._convert(data["unit"])),
            psr=float(StockInfo._convert(data["psr"])),
            per=float(StockInfo._convert(data["per"])),
            pbr=float(StockInfo._convert(data["pbr"])),
            volume=int(StockInfo._convert(data["volume"])),
            market_capitalization=data["market_capitalization"],
            issued_shares=data["issued_shares"],
            dt=data["date"],
        )

    @staticmethod
    def _convert(input_value: str) -> str:
        if input_value == "---":
            return "0"
        return input_value.replace("円", "").replace("株", "").replace("倍", "").replace(",", "")

    def dumps(self) -> dict:
        return asdict(self)
