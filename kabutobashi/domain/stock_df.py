from dataclasses import dataclass

import pandas as pd

from kabutobashi.errors import StockDfError


@dataclass(frozen=True)
class StockDf:
    data_df: pd.DataFrame
    REQUIRED_COL = ["open", "high", "low", "close"]

    def __post_init__(self):
        self._null_check()
        self._code_constraint_check()

    def _null_check(self):
        if self.data_df is None:
            raise StockDfError("required")

    def _code_constraint_check(self):
        df_columns = self.data_df.columns
        if "code" in df_columns:
            code = list(set(self.data_df.code.values))
            if len(code) > 1:
                raise StockDfError("multiple code")
            elif len(code) == 0:
                raise StockDfError("no code")

    def _required_column_check(self):
        columns = list(self.data_df.columns)
        # 必須のカラム確認
        if not all([item in columns for item in self.REQUIRED_COL]):
            raise StockDfError(f"required: {self.REQUIRED_COL}, input: {columns}")

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
            raise StockDfError("日付のカラム[dt, date]のいずれかが存在しません")
        if "date" in df_columns and "dt" in df_columns:
            raise StockDfError("日付のカラム[dt, date]は片方しか存在できません")

        # indexにdateを指定
        df.index = pd.to_datetime(df[date_column]).sort_index()

        # 必要なカラムに絞る
        df = df[StockDf.REQUIRED_COL]
        open_s = df["open"].apply(StockDf._replace_comma)
        close_s = df["close"].apply(StockDf._replace_comma)
        high_s = df["high"].apply(StockDf._replace_comma)
        low_s = df["low"].apply(StockDf._replace_comma)
        return StockDf(data_df=pd.DataFrame({"open": open_s, "high": high_s, "low": low_s, "close": close_s}))

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
            raise StockDfError(f"floatに変換できる値ではありません。{e}")
        return f
