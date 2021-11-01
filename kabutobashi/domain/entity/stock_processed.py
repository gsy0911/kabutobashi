from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

import pandas as pd


@dataclass(frozen=True)
class StockProcessed:
    """
    methodで処理した後のデータを保持
    可視化などを実行する際に利用

    """

    code: Optional[Union[str, int]]
    base_df: pd.DataFrame = field(repr=False)
    # {"method": "", "data": "", "color_mapping": List[dict]}
    processed_dfs: List[Dict[str, pd.DataFrame]] = field(repr=False)

    REQUIRED_DF_COLUMNS = ["code", "open", "close", "high", "low", "dt"]
    PROCESSED_SCHEMA = {
        "method": {"type": "string"},
        "data": {"required": True},
        "color_mapping": {"type": "list", "schema": {"type": "dict"}},
    }

    @staticmethod
    def of(_df: pd.DataFrame, methods: list) -> "StockProcessed":
        from kabutobashi.domain.method import Method

        # check all methods
        for method in methods:
            if not isinstance(method, Method):
                raise ValueError()

        initial_method: Method = methods[0]
        rest_methods: List[Method] = methods[1:]
        base = initial_method.process(_df=_df)

        for rest_method in rest_methods:
            base = base + rest_method.process(_df=_df)
        return base

    def _validate(self):
        columns = list(self.base_df.columns)
        # 必須のカラム確認
        if not all([item in columns for item in self.REQUIRED_DF_COLUMNS]):
            return KabutobashiEntityError(columns)

        validator = Validator(self.PROCESSED_SCHEMA)
        if not validator.validate(self.processed_dfs):
            raise KabutobashiEntityError(validator)

    def __add__(self, other: "StockProcessed") -> "StockProcessed":
        if not isinstance(other, StockProcessed):
            raise ValueError()

        # update
        processed_dfs = []
        processed_dfs.extend(self.processed_dfs)
        processed_dfs.extend(other.processed_dfs)
        return StockProcessed(
            code=self.code,
            base_df=self.base_df,
            processed_dfs=processed_dfs,
        )

    def get_impact(self, influence: int = 2, tail: int = 5) -> dict:
        """

        Args:
            influence:
            tail:

        Returns:
            Dict[str, float]

        Examples:
            >>> import kabutobashi as kb
            >>> df = kb.read_csv(...)
            >>> processed = kb.StockProcessed.of(_df=df, methods=[kb.sma, kb.macd])
            >>> processed.get_impact()
            {"sma": 0.4, "macd": -0.04}
            >>> sma = kb.SMA(short_term=3, medium_term=15, long_term=50)
            >>> processed = kb.StockProcessed.of(_df=df, methods=[sma, kb.macd])
            >>> processed.get_impact()
            {"sma": 0.2, "macd": -0.04}
        """
        result_dict = {}
        for v in self.processed_dfs:
            result_dict.update({
                v['method']: self._get_impact(_df=v['data'], influence=influence, tail=tail)
            })
        return result_dict

    @staticmethod
    def _get_impact(_df: pd.DataFrame, influence: int, tail: int) -> float:
        """
        売りと買いのシグナルの余波の合計値を返す。

        Args:
            _df:
            influence:
            tail:

        Returns:
            [-1,1]の値をとる。-1: 売り、1: 買いを表す
        """
        _df["buy_impact"] = _df["buy_signal"].ewm(span=influence).mean()
        _df["sell_impact"] = _df["sell_signal"].ewm(span=influence).mean()
        buy_impact_index = _df["buy_impact"].iloc[-tail:].sum()
        sell_impact_index = _df["sell_impact"].iloc[-tail:].sum()
        return round(buy_impact_index - sell_impact_index, 5)
