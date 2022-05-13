from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Generator, Set, List, NoReturn, Tuple, Union

import pandas as pd
from pydantic import BaseModel, Field

from kabutobashi.domain.errors import KabutobashiEntityError

REQUIRED_COL = ["code", "open", "close", "high", "low", "volume", "per", "psr", "pbr", "dt"]
OPTIONAL_COL = ["name", "industry_type", "market", "unit"]


def _replace(input_value: str) -> str:
    return input_value.replace("---", "0").replace("円", "").replace("株", "").replace("倍", "").replace(",", "")


def _convert_float(input_value: Union[str, float, int]) -> float:
    if type(input_value) == float or type(input_value) == int:
        return float(input_value)
    try:
        return float(_replace(input_value=input_value))
    except ValueError as e:
        raise KabutobashiEntityError(f"floatに変換できる値ではありません。{e}")


def _convert_int(input_value: Union[str, float, int]) -> int:
    if type(input_value) == float or type(input_value) == int:
        return int(input_value)
    try:
        return int(_replace(input_value=input_value))
    except ValueError as e:
        raise KabutobashiEntityError(f"floatに変換できる値ではありません。{e}")


class StockBrand(BaseModel):
    code: str
    unit: int
    market: str
    name: str
    industry_type: str
    market_capitalization: str
    issued_shares: str

    @staticmethod
    def loads(data: dict) -> "StockBrand":
        return StockBrand(
            code=str(data["code"]),
            unit=_convert_int(data["unit"]),
            market=data.get("market", ""),
            name=data.get("name", ""),
            industry_type=data.get("industry_type", ""),
            market_capitalization=data.get("market_capitalization", ""),
            issued_shares=data.get("issued_shares", ""),
        )

    def is_reit(self) -> bool:
        return self.market == "東証REIT"

    def __eq__(self, other):
        if not isinstance(other, StockBrand):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


class StockRecord(BaseModel):
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

    # TODO implements id_: str
    code: str
    open: float
    high: float
    low: float
    close: float
    psr: float
    per: float
    pbr: float
    volume: int
    dt: str

    @staticmethod
    def from_page_of(data: dict) -> "StockRecord":
        label_split = data["stock_label"].split("  ")
        try:
            return StockRecord(
                code=label_split[0],
                open=_replace(data["open"]),
                high=_replace(data["high"]),
                low=_replace(data["low"]),
                close=_replace(data["close"]),
                unit=_replace(data["unit"]),
                psr=_replace(data["psr"]),
                per=_replace(data["per"]),
                pbr=_replace(data["pbr"]),
                volume=_replace(data["volume"]),
                dt=data["date"],
            )
        except Exception:
            return StockRecord(
                code="",
                open=0,
                high=0,
                low=0,
                close=0,
                psr=0,
                per=0,
                pbr=0,
                volume=0,
                dt="",
            )

    def is_outlier(self) -> bool:
        return self.open == 0 or self.high == 0 or self.low == 0 or self.close == 0

    def dumps(self) -> dict:
        return self.dict()

    @staticmethod
    def loads(data: dict) -> "StockRecord":

        data_date = data.get("date")
        data_dt = data.get("dt")
        data_crawl_datetime = data.get("crawl_datetime")

        if data_date and data_dt and data_crawl_datetime:
            raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかしか選べません")
        if data_date:
            dt = data_date
        elif data_dt:
            dt = data_dt
        elif data_crawl_datetime:
            dt = datetime.fromisoformat(data_crawl_datetime).strftime("%Y-%m-%d")
        else:
            raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかが存在しません")

        return StockRecord(
            code=str(data["code"]),
            open=_convert_float(data["open"]),
            high=_convert_float(data["high"]),
            low=_convert_float(data["low"]),
            close=_convert_float(data["close"]),
            psr=_convert_float(data["psr"]),
            per=_convert_float(data["per"]),
            pbr=_convert_float(data["pbr"]),
            volume=data["volume"],
            dt=dt,
        )


class StockRecordset(BaseModel):
    brand_set: Set[StockBrand] = Field(repr=False)
    recordset: List[StockRecord] = Field(repr=False)

    def __post_init__(self):
        if not self.recordset:
            raise KabutobashiEntityError(f"required stock_data")

    @staticmethod
    def of(df: pd.DataFrame) -> "StockRecordset":
        recordset = []
        brand_set = set()
        for _, row in df.iterrows():
            recordset.append(StockRecord.loads(dict(row)))
            brand_set.add(StockBrand.loads(data=dict(row)))
        return StockRecordset(brand_set=brand_set, recordset=recordset)

    def get_code_list(self) -> List[str]:
        return list(set([v.code for v in self.recordset]))

    def _to_df(self) -> pd.DataFrame:
        df = pd.DataFrame([v.dumps() for v in self.recordset])
        df = df.convert_dtypes()
        # order by dt
        idx = pd.to_datetime(df["dt"]).sort_index()
        df.index = idx
        df = df.sort_index()
        return df

    def to_df(self, minimum=True, latest=False):
        df = self._to_df()

        if latest:
            latest_dt = max(df["dt"])
            df = df[df["dt"] == latest_dt]

        if minimum:
            return df[REQUIRED_COL]
        else:
            return df[REQUIRED_COL + OPTIONAL_COL]


class IStockRecordsetRepository(metaclass=ABCMeta):
    def read(self) -> "StockRecordset":
        return self._stock_recordset_read()

    @abstractmethod
    def _stock_recordset_read(self) -> "StockRecordset":
        raise NotImplementedError()

    def write(self, data: StockRecordset) -> NoReturn:
        self._stock_recordset_write(data=data)

    @abstractmethod
    def _stock_recordset_write(self, data: StockRecordset) -> NoReturn:
        raise NotImplementedError()


class StockDataSingleCode(BaseModel):
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

    Examples:
        >>> import kabutobashi as kb
        >>> import pandas as pd
        >>> data_list = []
        >>> sdmc = kb.example()
        >>> parameterize_methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
        >>> for sdsc in sdmc.to_code_iterable(until=1, row_more_than=80):
        >>>     code = sdsc.code
        >>>     print(code)
        >>>     for idx, df_x, df_y in sdsc.sliding_split():
        >>>         df_params = kb.StockDataAnalyzedByMultipleMethod.of(df=df_x, methods=parameterize_methods)
        >>>         # diff:= df_y.last - df_x.last
        >>>         start = list(df_x["close"])[-1]
        >>>         end = list(df_y["close"])[-1]
        >>>         diff = end - start
        >>>         d = df_params.get_parameters()
        >>>         d.update({"diff": diff})
        >>>         data_list.append(d)
        >>>  data_for_ml = pd.DataFrame(data_list)

    """

    code: str
    stop_updating: bool
    contains_outlier: bool
    stock_recordset: StockRecordset
    len_: int

    def __post_init__(self):
        self._code_constraint_check(stock_recordset=self.stock_recordset)

    @staticmethod
    def _code_constraint_check(stock_recordset: StockRecordset):
        code = stock_recordset.get_code_list()
        if len(code) > 1:
            raise KabutobashiEntityError("multiple code")
        elif len(code) == 0:
            raise KabutobashiEntityError("no code")

    @staticmethod
    def of(df: pd.DataFrame):
        recordset = StockRecordset.of(df=df)

        # codeの確認
        StockDataSingleCode._code_constraint_check(stock_recordset=recordset)
        code = recordset.get_code_list()[0]
        return StockDataSingleCode(
            code=code,
            stock_recordset=recordset,
            stop_updating=StockDataSingleCode._check_recent_update(df=df),
            contains_outlier=any([v.is_outlier() for v in recordset.recordset]),
            len_=len(recordset.recordset),
        )

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
            df_for_y: ``buy_sell_term_days`` 後のDataFrameを返す。値動きを追うため。
        """
        df = self.to_df()
        df_length = len(df.index)
        if df_length < buy_sell_term_days + sliding_window:
            raise KabutobashiEntityError("入力されたDataFrameの長さがwindow幅よりも小さいです")
        loop = df_length - (buy_sell_term_days + sliding_window)
        for idx, i in enumerate(range(0, loop, step)):
            offset = i + sliding_window
            end = offset + buy_sell_term_days
            yield idx, df[i:offset], df[offset:end]

    def to_df(self, minimum=True, latest=False) -> pd.DataFrame:
        return self.stock_recordset.to_df(minimum=minimum, latest=latest)

    def __len__(self):


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
        >>> sdsc = sdmc.to_single_code(code="1375")
    """

    df: pd.DataFrame
    REQUIRED_COL = StockRecordset.REQUIRED_COL
    OPTIONAL_COL = StockRecordset.OPTIONAL_COL
    # TODO implements stock_data_single_code_list: List[StockDataSingleCode]

    def __post_init__(self):
        self._null_check()
        if not self._validate():
            raise KabutobashiEntityError(f"不正なデータ構造です: {self.df.columns=}")
        self._convert_df_types()

    def _null_check(self):
        if self.df is None:
            raise KabutobashiEntityError("required")

    def _validate(self) -> bool:
        columns = list(self.df.columns)
        # 必須のカラム確認
        if not all([item in columns for item in self.REQUIRED_COL]):
            return False
        return True

    def _convert_df_types(self):
        self.df["code"] = self.df["code"].astype(str)

    @staticmethod
    def of(df: pd.DataFrame) -> "StockDataMultipleCode":
        return StockDataMultipleCode(df=df)

    def to_single_code(self, code: str) -> StockDataSingleCode:
        if type(code) is not str:
            raise KabutobashiEntityError(f"code must be type of `str`")
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

            # create sdsc
            sdsc = StockDataSingleCode.of(df=df_)
            if sdsc.stop_updating:
                continue
            if sdsc.contains_outlier:
                continue

            # add counter if yield
            if until:
                if _count >= until:
                    return
            _count += 1

            yield sdsc

    def get_df(self, minimum=True, latest=False, code_list: list = None) -> pd.DataFrame:
        """
        returns column-formatted DataFrame.

        Args:
            minimum:
            latest:
            code_list: filters specified code, default None.

        Returns:
            pd.DataFrame
        """
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

    @staticmethod
    def read(use_mp: bool = False, max_workers: int = 2):
        """

        Args:
            use_mp: default False.
            max_workers: default 2.

        Returns:
            StockDataMultipleCodeReader
        """
        from kabutobashi.infrastructure.repository.stock_data_repository import StockDataMultipleCodeReader

        return StockDataMultipleCodeReader(use_mp=use_mp, max_workers=max_workers)

    @staticmethod
    def crawl(use_mp: bool = False, max_workers: int = 2):
        """

        Args:
            use_mp: default False.
            max_workers: default 2.

        Returns:
            StockDataMultipleCodeCrawler
        """
        from kabutobashi.infrastructure.repository.stock_data_repository import StockDataMultipleCodeCrawler

        return StockDataMultipleCodeCrawler(use_mp=use_mp, max_workers=max_workers)

    def write(self):
        """

        Returns:
            StockDataMultipleCodeWriter
        """
        from kabutobashi.infrastructure.repository.stock_data_repository import StockDataMultipleCodeWriter

        return StockDataMultipleCodeWriter(multiple_code=self)
