from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from kabutobashi.domain.errors import KabutobashiEntityError


class StockDataProcessed(BaseModel):
    """
    StockDataProcessed: ValueObject
    Holds data processed by singular-Method.
    """

    code: str
    start_at: str
    end_at: str
    applied_method_name: str
    df: pd.DataFrame = Field(repr=False)
    df_required_columns: List[str] = Field(repr=False)
    parameters: Dict[str, Any]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    @field_validator("df")
    def _validate_df(cls, v, info: FieldValidationInfo):
        df_required_columns = info.data["df_required_columns"]
        df_columns = v.columns
        if not all([c in df_columns for c in df_required_columns]):
            raise KabutobashiEntityError()


class StockDataVisualized(BaseModel):
    """
    StockDataVisualized: ValueObject
    Used to visualize.
    """

    fig: plt.Figure
    size_ratio: int
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    @field_validator("fig")
    def _validate_fig(cls, v):
        if type(v) is not plt.Figure:
            raise KabutobashiEntityError()


class StockDataEstimated(BaseModel):
    """
    StockDataEstimated: ValueObject
    """

    code: str
    estimated_value: float
    estimate_filter_name: str

    def weighted_estimated_value(self, weights: dict) -> float:
        weight = weights.get(self.estimate_filter_name, 1)
        return weight * self.estimated_value
