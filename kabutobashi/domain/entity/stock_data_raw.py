from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Generator, Optional, Tuple, Union

import pandas as pd
from cerberus import Validator

from kabutobashi.errors import KabutobashiEntityError

from .stock_data_processed import StockDataProcessed


@dataclass(frozen=True)
class StockDataSingleDay:
    """

    * code: 銘柄コード
    * open: 始値
    * close: 終値
    * high: 高値
    * low: 底値
    * unit: 単位
    * volume: 出来高
    * per: PER
    * psr: PSR
    * pbr: PBR
    * market: 市場
    * dt: その株価の値の日
    * name: 名前
    * industry_type: 業種

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
        return input_value.replace("---", "0").replace("円", "").replace("株", "").replace("倍", "").replace(",", "")

    def dumps(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class StockDataSingleCode:
    """
    単一銘柄の複数日の株データを保持するEntity

    以下のデータを保持する

    * code: 銘柄コード
    * open: 始値
    * close: 終値
    * high: 高値
    * low: 底値
    * unit: 単位
    * volume: 出来高
    * per: PER
    * psr: PSR
    * pbr: PBR
    * market: 市場
    * dt: その株価の値の日
    * name: 名前
    * industry_type: 業種

    Args:
        df: 複数日・単一銘柄を保持するDataFrame
        code: 銘柄コード

    """

    df: pd.DataFrame
    code: str
    stop_updating: bool
    contains_outlier: bool
    REQUIRED_COL = ["code", "open", "close", "high", "low", "unit", "volume", "per", "psr", "pbr", "market", "dt"]
    OPTIONAL_COL = ["name", "industry_type"]

    def __post_init__(self):
        self._null_check()
        self._code_constraint_check(df=self.df)
        if not self._validate():
            raise KabutobashiEntityError(f"required: {self.REQUIRED_COL}, input: {self.df.columns}")

    def _null_check(self):
        if self.df is None:
            raise KabutobashiEntityError("required")

    def _validate(self) -> bool:
        columns = list(self.df.columns)
        # 必須のカラム確認
        if not all([item in columns for item in self.REQUIRED_COL]):
            return False
        return True

    @staticmethod
    def _code_constraint_check(df: pd.DataFrame):
        df_columns = df.columns
        if "code" in df_columns:
            code = list(set(df.code.values))
            if len(code) > 1:
                raise KabutobashiEntityError("multiple code")
            elif len(code) == 0:
                raise KabutobashiEntityError("no code")

    @staticmethod
    def of(df: pd.DataFrame):
        df_columns = df.columns
        # 日付カラムの候補値を探す
        date_column = None
        if "date" in df_columns:
            date_column = "date"
        elif "dt" in df_columns:
            date_column = "dt"
        elif "crawl_datetime" in df_columns:
            date_column = "crawl_datetime"
        if date_column is None:
            raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかが存在しません")
        if ("date" in df_columns) and ("dt" in df_columns) and ("crawl_datetime" in df_columns):
            raise KabutobashiEntityError("日付のカラム[dt, date]は片方しか存在できません")

        # 変換
        if date_column == "crawl_datetime":
            df["dt"] = df["crawl_datetime"].apply(lambda x: datetime.fromisoformat(x).strftime("%Y-%m-%d"))
            date_column = "dt"
        # indexにdateを指定
        idx = pd.to_datetime(df[date_column]).sort_index()

        # codeの確認
        StockDataSingleCode._code_constraint_check(df=df)
        if "code" in df_columns:
            code = list(set(df.code.values))[0]
        else:
            code = "-"

        # 数値に変換・「業種」という文字列削除
        df = df.assign(
            open=df["open"].apply(StockDataSingleCode._replace_comma),
            close=df["close"].apply(StockDataSingleCode._replace_comma),
            high=df["high"].apply(StockDataSingleCode._replace_comma),
            low=df["low"].apply(StockDataSingleCode._replace_comma),
            pbr=df["pbr"].apply(StockDataSingleCode._replace_comma),
            psr=df["psr"].apply(StockDataSingleCode._replace_comma),
            per=df["per"].apply(StockDataSingleCode._replace_comma),
        )
        if "industry_type" in df_columns:
            df["industry_type"] = df["industry_type"].apply(lambda x: x.replace("業種", ""))

        df.index = idx
        df = df.fillna(0)
        df = df.convert_dtypes()
        return StockDataSingleCode(
            code=code,
            df=df,
            stop_updating=StockDataSingleCode._check_recent_update(df=df),
            contains_outlier=StockDataSingleCode._check_outlier_value(df=df),
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

    @staticmethod
    def _check_recent_update(df: pd.DataFrame) -> bool:
        """
        直近の更新が止まっているかどうか
        """
        return (
            (len(df["open"].tail(10).unique()) == 1)
            or (len(df["high"].tail(10).unique()) == 1)
            or (len(df["low"].tail(10).unique()) == 1)
            or (len(df["close"].tail(10).unique()) == 1)
        )

    @staticmethod
    def _check_outlier_value(df: pd.DataFrame) -> bool:
        """
        不正な値が含まれている場合にtrueを返す

        以下の場合にTrueになる
        - 急に0になる値が含まれている
        """
        return (
            (len(df[df["open"] == 0].index) > 0)
            or (len(df[df["high"] == 0].index) > 0)
            or (len(df[df["low"] == 0].index) > 0)
            or (len(df[df["close"] == 0].index) > 0)
        )

    def sliding_split(
        self, *, buy_sell_term_days: int = 5, sliding_window: int = 60, step: int = 3
    ) -> Generator[Tuple[int, pd.DataFrame, pd.DataFrame], None, None]:
        """
        単一の銘柄に関してwindow幅を ``sliding_window`` 日として、
        保持しているデータの期間の間をslidingしていく関数。

        Args:
            buy_sell_term_days: この日数後までデータを切り出す。
            sliding_window: slidingしていくwindow幅
            step: windowsをずらしていく期間

        Returns:
            idx: 切り出された番号。
            df_for_x: 特徴量を計算するためのDataFrame。
            df_for_y: `buy_sell_term_days`後のDataFrameを返す。値動きを追うため。
        """
        df_length = len(self.df.index)
        if df_length < buy_sell_term_days + sliding_window:
            raise KabutobashiEntityError("入力されたDataFrameの長さがwindow幅よりも小さいです")
        loop = df_length - (buy_sell_term_days + sliding_window)
        for idx, i in enumerate(range(0, loop, step)):
            offset = i + sliding_window
            end = offset + buy_sell_term_days
            yield idx, self.df[i:offset], self.df[offset:end]

    def get_df(self, minimum=True, latest=False):
        df = self.df

        if latest:
            latest_dt = max(df["dt"])
            df = df[df["dt"] == latest_dt]

        if minimum:
            return df[self.REQUIRED_COL]
        else:
            return df[self.REQUIRED_COL + self.OPTIONAL_COL]

    def to_processed(self, methods: list) -> StockDataProcessed:
        return StockDataProcessed.of(df=self.df, methods=methods)

    def to_parameterize(self, methods: list):
        pass


@dataclass(frozen=True)
class StockDataMultipleCode:
    """
    複数銘柄の複数日の株データを保持するEntity

    単一銘柄のデータのみを返したり、複数銘柄のデータをループで取得できるクラス。

    Args:
        df: 複数日・複数銘柄を保持するDataFrame

    Examples:
        >>> import kabutobashi as kb
        >>> sdmc = kb.example()
        >>> sdsc = sdmc.to_single_code(code=1375)
    """

    df: pd.DataFrame
    REQUIRED_COL = StockDataSingleCode.REQUIRED_COL
    OPTIONAL_COL = StockDataSingleCode.OPTIONAL_COL

    def __post_init__(self):
        self._null_check()
        if not self._validate():
            raise KabutobashiEntityError(f"不正なデータ構造です: {self.df.columns=}")

    def _null_check(self):
        if self.df is None:
            raise KabutobashiEntityError("required")

    def _validate(self) -> bool:
        columns = list(self.df.columns)
        # 必須のカラム確認
        if not all([item in columns for item in self.REQUIRED_COL]):
            return False
        return True

    @staticmethod
    def of(df: pd.DataFrame) -> "StockDataMultipleCode":
        return StockDataMultipleCode(df=df)

    def to_single_code(self, code: Union[str, int]) -> StockDataSingleCode:
        return StockDataSingleCode.of(df=self.df[self.df["code"] == code])

    def to_code_iterable(
        self,
        until: Optional[int] = None,
        *,
        skip_reit: bool = True,
        row_more_than: Optional[int] = 80,
        code_list: list = None,
    ) -> Generator[StockDataSingleCode, None, None]:
        _count = 0
        df = self.df.copy()

        if code_list:
            df = df[df["code"].isin(code_list)]
        if skip_reit:
            df = df[~(df["market"] == "東証REIT")]

        for code, df_ in df.groupby("code"):
            if row_more_than:
                if len(df_.index) < row_more_than:
                    continue
            if until:
                if _count >= until:
                    return
            _count += 1

            sdsc = StockDataSingleCode.of(df=df_)
            if sdsc.stop_updating:
                continue
            if sdsc.contains_outlier:
                continue
            yield sdsc

    def get_df(self, minimum=True, latest=False, code_list: list = None):
        df = self.df

        if code_list:
            df = df[df["code"].isin(code_list)]
        if latest:
            latest_dt = max(df["dt"])
            df = df[df["dt"] == latest_dt]

        if minimum:
            return df[self.REQUIRED_COL]
        else:
            return df[self.REQUIRED_COL + self.OPTIONAL_COL]
