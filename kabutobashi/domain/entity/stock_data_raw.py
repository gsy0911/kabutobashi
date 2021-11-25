from dataclasses import asdict, dataclass

import pandas as pd
from cerberus import Validator

from kabutobashi.errors import KabutobashiEntityError


@dataclass(frozen=True)
class StockDataSingleDay:
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
        return list(StockDataSingleDay._SCHEMA.keys())

    @staticmethod
    def from_page_of(data: dict) -> "StockDataSingleDay":
        label_split = data["stock_label"].split("  ")
        return StockDataSingleDay(
            code=label_split[0],
            market=label_split[1],
            name=data["name"],
            industry_type=data["industry_type"],
            open=float(StockDataSingleDay._convert(data["open"])),
            high=float(StockDataSingleDay._convert(data["high"])),
            low=float(StockDataSingleDay._convert(data["low"])),
            close=float(StockDataSingleDay._convert(data["close"])),
            unit=int(StockDataSingleDay._convert(data["unit"])),
            psr=float(StockDataSingleDay._convert(data["psr"])),
            per=float(StockDataSingleDay._convert(data["per"])),
            pbr=float(StockDataSingleDay._convert(data["pbr"])),
            volume=int(StockDataSingleDay._convert(data["volume"])),
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


@dataclass(frozen=True)
class StockDataSingleCode:
    data_df: pd.DataFrame
    code: str
    REQUIRED_COL = ["open", "high", "low", "close"]

    def __post_init__(self):
        self._null_check()
        self._code_constraint_check(df=self.data_df)

    def _null_check(self):
        if self.data_df is None:
            raise KabutobashiEntityError("required")

    @staticmethod
    def _code_constraint_check(df: pd.DataFrame):
        df_columns = df.columns
        if "code" in df_columns:
            code = list(set(df.code.values))
            if len(code) > 1:
                raise KabutobashiEntityError("multiple code")
            elif len(code) == 0:
                raise KabutobashiEntityError("no code")

    def _required_column_check(self):
        columns = list(self.data_df.columns)
        # 必須のカラム確認
        if not all([item in columns for item in self.REQUIRED_COL]):
            raise KabutobashiEntityError(f"required: {self.REQUIRED_COL}, input: {columns}")

    @staticmethod
    def of(df: pd.DataFrame):
        df_columns = df.columns
        # 日付カラムの候補値を探す
        date_column = None
        if "date" in df_columns:
            date_column = "date"
        elif "dt" in df_columns:
            date_column = "dt"
        if date_column is None:
            raise KabutobashiEntityError("日付のカラム[dt, date]のいずれかが存在しません")
        if "date" in df_columns and "dt" in df_columns:
            raise KabutobashiEntityError("日付のカラム[dt, date]は片方しか存在できません")

        # codeの確認
        StockDataSingleCode._code_constraint_check(df=df)
        code = list(set(df.code.values))[0]

        # indexにdateを指定
        idx = pd.to_datetime(df[date_column]).sort_index()

        # 必要なカラムに絞る
        df = df[StockDataSingleCode.REQUIRED_COL]
        open_s = df["open"].apply(StockDataSingleCode._replace_comma)
        close_s = df["close"].apply(StockDataSingleCode._replace_comma)
        high_s = df["high"].apply(StockDataSingleCode._replace_comma)
        low_s = df["low"].apply(StockDataSingleCode._replace_comma)
        return StockDataSingleCode(
            code=code,
            data_df=pd.DataFrame(data={"open": open_s, "high": high_s, "low": low_s, "close": close_s}, index=idx)
        )

    @staticmethod
    def _replace_comma(x) -> float:
        """
        pandas内の値がカンマ付きの場合に、カンマを削除する関数
        :param x:
        :return:
        """
        if type(x) is str:
            x = x.replace(",", "")
        try:
            f = float(x)
        except ValueError as e:
            raise KabutobashiEntityError(f"floatに変換できる値ではありません。{e}")
        return f


@dataclass(frozen=True)
class StockDataMultipleCode:
    pass
