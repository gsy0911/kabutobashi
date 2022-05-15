from dataclasses import dataclass, field
from typing import Any, Dict, List

import pandas as pd
from cerberus import Validator

from kabutobashi.domain.errors import KabutobashiEntityError


@dataclass(frozen=True)
class StockDataProcessedBySingleMethod:
    """
    StockDataProcessedBySingleMethod: ValueObject
    Holds data processed by singular-Method.
    """

    code: str
    start_at: str
    end_at: str
    applied_method_name: str
    df: pd.DataFrame = field(repr=False)
    df_required_columns: List[str] = field(repr=False)
    parameters: Dict[str, Any]
    color_mapping: list = field(repr=False)
    visualize_option: dict = field(repr=False)
    COLOR_MAPPING_SCHEMA = {
        "df_key": {"type": "string"},
        "color": {"type": "string"},
        "label": {"type": "string"},
        "plot": {"type": "string", "allowed": ["plot", "bar"], "required": False},
    }
    VISUALIZE_OPTION_SCHEMA = {"position": {"type": "string", "allowed": ["in", "lower", "-"]}}

    def __post_init__(self):
        self._check_color_mapping(data=self.color_mapping)
        self._check_visualize_option(data=self.visualize_option)

    def _check_color_mapping(self, data: list):
        validator = Validator(self.COLOR_MAPPING_SCHEMA)
        for d in data:
            if not validator.validate(d):
                raise KabutobashiEntityError(validator)

    def _check_visualize_option(self, data: dict):
        validator = Validator(self.VISUALIZE_OPTION_SCHEMA)
        if not validator.validate(data):
            raise KabutobashiEntityError(validator)

    def get_impact(self, influence: int = 2, tail: int = 5) -> Dict[str, float]:
        """

        Args:
            influence:
            tail:

        Returns:
            Dict[str, float]

        Examples:
        """
        return {self.applied_method_name: self._get_impact(df=self.df, influence=influence, tail=tail)}

    @staticmethod
    def _get_impact(df: pd.DataFrame, influence: int, tail: int) -> float:
        """
        売りと買いのシグナルの余波の合計値を返す。

        Args:
            df:
            influence:
            tail:

        Returns:
            [-1,1]の値をとる。-1: 売り、1: 買いを表す
        """
        df["buy_impact"] = df["buy_signal"].ewm(span=influence).mean()
        df["sell_impact"] = df["sell_signal"].ewm(span=influence).mean()
        buy_impact_index = df["buy_impact"].iloc[-tail:].sum()
        sell_impact_index = df["sell_impact"].iloc[-tail:].sum()
        return round(buy_impact_index - sell_impact_index, 5)
