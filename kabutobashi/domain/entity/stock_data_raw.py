from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Generator, List, Optional, Tuple, Union

import pandas as pd
from cerberus import Validator

from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.services.estimate_filter import EstimateFilter
from kabutobashi.domain.services.method import Method

from .stock_data_estimated import StockDataEstimatedByMultipleFilter
from .stock_data_processed import StockDataProcessedByMultipleMethod, StockDataProcessedBySingleMethod


@dataclass(frozen=True)
class StockData:
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
        "open": {"type": "number"},
        "high": {"type": "number"},
        "low": {"type": "number"},
        "close": {"type": "number"},
        "psr": {"type": "number"},
        "per": {"type": "number"},
        "pbr": {"type": "number"},
        "volume": {"type": "number"},
        "unit": {"type": "number"},
        "market_capitalization": {"type": "string"},
        "issued_shares": {"type": "string"},
        "dt": {"type": "string"},
    }

    def __post_init__(self):
        validator = Validator(self._SCHEMA)
        if not validator.validate(self.dumps()):
            raise KabutobashiEntityError(validator.errors)

    @staticmethod
    def schema() -> list:
        return list(StockData._SCHEMA.keys())

    @staticmethod
    def from_page_of(data: dict) -> "StockData":
        label_split = data["stock_label"].split("  ")
        try:
            return StockData(
                code=label_split[0],
                market=label_split[1],
                name=data["name"],
                industry_type=data["industry_type"],
                open=float(StockData._convert(data["open"])),
                high=float(StockData._convert(data["high"])),
                low=float(StockData._convert(data["low"])),
                close=float(StockData._convert(data["close"])),
                unit=int(StockData._convert(data["unit"])),
                psr=float(StockData._convert(data["psr"])),
                per=float(StockData._convert(data["per"])),
                pbr=float(StockData._convert(data["pbr"])),
                volume=int(StockData._convert(data["volume"])),
                market_capitalization=data["market_capitalization"],
                issued_shares=data["issued_shares"],
                dt=data["date"],
            )
        except Exception:
            return StockData(
                code="",
                market="",
                name="",
                industry_type="",
                open=0,
                high=0,
                low=0,
                close=0,
                unit=0,
                psr=0,
                per=0,
                pbr=0,
                volume=0,
                market_capitalization="",
                issued_shares="",
                dt="",
            )

    def is_outlier(self) -> bool:
        return self.open == 0 or self.high == 0 or self.low == 0 or self.close == 0

    @staticmethod
    def _convert(input_value: str) -> str:
        return input_value.replace("---", "0").replace("円", "").replace("株", "").replace("倍", "").replace(",", "")

    @staticmethod
    def _convert_float(input_value: Union[str, float, int]) -> float:
        if type(input_value) == float or type(input_value) == int:
            return input_value
        try:
            return float(StockData._convert(input_value=input_value))
        except ValueError as e:
            raise KabutobashiEntityError(f"floatに変換できる値ではありません。{e}")

    @staticmethod
    def _convert_int(input_value: Union[str, float, int]) -> int:
        if type(input_value) == float or type(input_value) == int:
            return input_value
        try:
            return int(StockData._convert(input_value=input_value))
        except ValueError as e:
            raise KabutobashiEntityError(f"floatに変換できる値ではありません。{e}")

    def dumps(self) -> dict:
        return asdict(self)

    @staticmethod
    def loads(data: dict) -> "StockData":
        return StockData(
            code=data["code"],
            market=data.get("market", ""),
            name=data.get("name", ""),
            industry_type=data.get("industry_type", ""),
            open=StockData._convert_float(data["open"]),
            high=StockData._convert_float(data["high"]),
            low=StockData._convert_float(data["low"]),
            close=StockData._convert_float(data["close"]),
            unit=StockData._convert_int(data["unit"]),
            psr=StockData._convert_float(data["psr"]),
            per=StockData._convert_float(data["per"]),
            pbr=StockData._convert_float(data["pbr"]),
            volume=data["volume"],
            market_capitalization=data.get("market_capitalization", ""),
            issued_shares=data.get("issued_shares", ""),
            dt=data["dt"],
        )


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

    # df: pd.DataFrame
    code: str
    stop_updating: bool
    contains_outlier: bool
    _stock_data_list: List[StockData] = field(default_factory=list, repr=False)
    REQUIRED_COL = ["code", "open", "close", "high", "low", "unit", "volume", "per", "psr", "pbr", "market", "dt"]
    OPTIONAL_COL = ["name", "industry_type"]

    def __post_init__(self):
        if not self._stock_data_list:
            raise KabutobashiEntityError(f"required stock_data")
        self._code_constraint_check(stock_data_list=self._stock_data_list)

    @staticmethod
    def _code_constraint_check(stock_data_list: List[StockData]):
        code = [v.code for v in stock_data_list]
        if len(set(code)) > 1:
            raise KabutobashiEntityError("multiple code")
        elif len(code) == 0:
            raise KabutobashiEntityError("no code")

    @staticmethod
    def of(df: pd.DataFrame):
        _stock_data_list = []
        for _, row in df.iterrows():
            _stock_data_list.append(StockData.loads(dict(row)))

        # df_columns = df.columns
        # # 日付カラムの候補値を探す
        # date_column = None
        # if "date" in df_columns:
        #     date_column = "date"
        # elif "dt" in df_columns:
        #     date_column = "dt"
        # elif "crawl_datetime" in df_columns:
        #     date_column = "crawl_datetime"
        # if date_column is None:
        #     raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかが存在しません")
        # if ("date" in df_columns) and ("dt" in df_columns) and ("crawl_datetime" in df_columns):
        #     raise KabutobashiEntityError("日付のカラム[dt, date]は片方しか存在できません")
        #
        # # 変換
        # if date_column == "crawl_datetime":
        #     df["dt"] = df["crawl_datetime"].apply(lambda x: datetime.fromisoformat(x).strftime("%Y-%m-%d"))
        #     date_column = "dt"
        # # indexにdateを指定
        # idx = pd.to_datetime(df[date_column]).sort_index()
        #
        # # codeの確認
        StockDataSingleCode._code_constraint_check(stock_data_list=_stock_data_list)
        code = _stock_data_list[0].code
        # if "code" in df_columns:
        #     code = list(set(df.code.values))[0]
        # else:
        #     code = "-"
        #
        # # 数値に変換・「業種」という文字列削除
        # df = df.assign(
        #     open=df["open"].apply(StockDataSingleCode._replace_comma),
        #     close=df["close"].apply(StockDataSingleCode._replace_comma),
        #     high=df["high"].apply(StockDataSingleCode._replace_comma),
        #     low=df["low"].apply(StockDataSingleCode._replace_comma),
        #     pbr=df["pbr"].apply(StockDataSingleCode._replace_comma),
        #     psr=df["psr"].apply(StockDataSingleCode._replace_comma),
        #     per=df["per"].apply(StockDataSingleCode._replace_comma),
        # )
        # if "industry_type" in df_columns:
        #     df["industry_type"] = df["industry_type"].apply(lambda x: x.replace("業種", ""))
        #
        # df.index = idx
        # df = df.fillna(0)
        # df = df.convert_dtypes()
        # # order by dt
        # df = df.sort_index()
        return StockDataSingleCode(
            code=code,
            _stock_data_list=_stock_data_list,
            stop_updating=StockDataSingleCode._check_recent_update(df=df),
            contains_outlier=any([v.is_outlier() for v in _stock_data_list])
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
        df = self._to_df()
        df_length = len(df.index)
        if df_length < buy_sell_term_days + sliding_window:
            raise KabutobashiEntityError("入力されたDataFrameの長さがwindow幅よりも小さいです")
        loop = df_length - (buy_sell_term_days + sliding_window)
        for idx, i in enumerate(range(0, loop, step)):
            offset = i + sliding_window
            end = offset + buy_sell_term_days
            yield idx, df[i:offset], df[offset:end]

    def _to_df(self) -> pd.DataFrame:
        return pd.DataFrame([v.dumps() for v in self._stock_data_list])

    def to_df(self, minimum=True, latest=False):
        df = self._to_df()

        if latest:
            latest_dt = max(df["dt"])
            df = df[df["dt"] == latest_dt]

        if minimum:
            return df[self.REQUIRED_COL]
        else:
            return df[self.REQUIRED_COL + self.OPTIONAL_COL]

    def _to_single_processed(self, method: Method) -> StockDataProcessedBySingleMethod:
        df = self._to_df()
        # 日時
        start_at = list(df["dt"])[0]
        end_at = list(df["dt"])[-1]

        # 必要なパラメータの作成
        columns = ["dt", "open", "close", "high", "low", "buy_signal", "sell_signal"] + method.processed_columns()
        df_p = df.pipe(method.method).pipe(method.signal).loc[:, columns]
        params = method.parameterize(df_x=df, df_p=df_p)

        return StockDataProcessedBySingleMethod(
            code=self.code,
            start_at=start_at,
            end_at=end_at,
            applied_method_name=method.method_name,
            df=df_p,
            df_required_columns=columns,
            parameters=params,
            color_mapping=method.color_mapping(),
            visualize_option=method.visualize_option(),
        )

    def to_processed(self, methods: List[Method]) -> StockDataProcessedByMultipleMethod:
        # check all methods
        for method in methods:
            if not isinstance(method, Method):
                raise KabutobashiEntityError()

        return StockDataProcessedByMultipleMethod(processed=[self._to_single_processed(m) for m in methods])


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
    REQUIRED_COL = StockDataSingleCode.REQUIRED_COL
    OPTIONAL_COL = StockDataSingleCode.OPTIONAL_COL
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

    def to_processed(
        self,
        methods: List[Method],
        until: Optional[int] = None,
        *,
        skip_reit: bool = True,
        row_more_than: Optional[int] = 80,
    ) -> Generator[StockDataProcessedByMultipleMethod, None, None]:
        """

        Args:
            methods:
            until:
            skip_reit:
            row_more_than:

        Returns:

        """
        for sdsc in self.to_code_iterable(until=until, skip_reit=skip_reit, row_more_than=row_more_than):
            yield sdsc.to_processed(methods=methods)

    def to_estimated(
        self,
        methods: List[Method],
        estimate_filters: List[EstimateFilter],
        until: Optional[int] = None,
        *,
        skip_reit: bool = True,
        row_more_than: Optional[int] = 80,
    ) -> Generator[StockDataEstimatedByMultipleFilter, None, None]:
        """

        Args:
            methods:
            estimate_filters:
            until:
            skip_reit:
            row_more_than:

        Returns:

        """
        for processed in self.to_processed(
            methods=methods, until=until, skip_reit=skip_reit, row_more_than=row_more_than
        ):
            yield processed.to_estimated(estimate_filters=estimate_filters)

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
