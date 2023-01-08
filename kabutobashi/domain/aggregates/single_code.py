from dataclasses import dataclass, field
from typing import List, Optional, Union

import pandas as pd

from kabutobashi.domain.entity import Stock
from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.serialize import IDictSerialize
from kabutobashi.domain.services.analyze import StockAnalysis
from kabutobashi.domain.services.method import Method
from kabutobashi.domain.values import StockDataEstimated, StockDataProcessed, StockDataVisualized

__all__ = ["StockCodeSingleAggregate"]


@dataclass(frozen=True)
class StockCodeSingleAggregate(IDictSerialize):
    """
    StockCodeSingleAggregate: Aggregate

    Examples:
        >>> import kabutobashi as kb
        >>> import pandas as pd
        >>> data_list = []
        >>> df = kb.example()
        >>> methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
        >>> stock_analysis = kb.stock_analysis
        >>>
        >>> agg = kb.StockCodeSingleAggregate.of(entity=df, code="1234")
        >>>     .with_processed(methods)
        >>>     .with_estimated(stock_analysis)
        >>> print(agg.weighted_estimated_value())
    """

    code: str
    stock: Stock
    processed_list: List[StockDataProcessed] = field(default_factory=list, repr=False)
    estimated_list: List[StockDataEstimated] = field(default_factory=list, repr=False)

    def __post_init__(self):
        pass

    @staticmethod
    def of(entity: Union[pd.DataFrame, Stock], *, code: Optional[str] = None) -> "StockCodeSingleAggregate":
        if type(entity) is pd.DataFrame:
            entity["code"] = entity["code"].astype(str)
            stock = Stock.from_df(data=entity[entity["code"] == code])
        elif type(entity) is Stock:
            stock = entity
        else:
            raise KabutobashiEntityError("accept pd.DataFrame or StockDataSingleCode")

        code = stock.code
        return StockCodeSingleAggregate(code=code, stock=stock)

    def with_processed(self, methods: List[Method]) -> "StockCodeSingleAggregate":
        # check all methods
        for method in methods:
            if not isinstance(method, Method):
                raise KabutobashiEntityError()

        df = self.stock.to_df()
        return StockCodeSingleAggregate(
            code=self.code,
            stock=self.stock,
            processed_list=[m.process_method.process(df=df) for m in methods],
        )

    def _to_single_estimated(self, stock_analysis: StockAnalysis) -> StockDataEstimated:
        def get_parameters():
            data_ = {}
            for a in self.processed_list:
                data_.update(a.parameters)
            return data_

        return StockDataEstimated(
            code=self.code,
            estimate_filter_name=stock_analysis.estimate_filter_name,
            estimated_value=stock_analysis.estimate(data=get_parameters()),
        )

    def with_estimated(self, stock_analysis: List[StockAnalysis]) -> "StockCodeSingleAggregate":
        """

        Returns:
            StockDataEstimatedByMultipleFilter
        """
        return StockCodeSingleAggregate(
            code=self.code,
            stock=self.stock,
            processed_list=self.processed_list,
            estimated_list=[self._to_single_estimated(stock_analysis=sa) for sa in stock_analysis],
        )

    def weighted_estimated_value(self, weights: dict = None) -> float:
        if not weights:
            weights = {}
        return sum([e.weighted_estimated_value(weights=weights) for e in self.estimated_list])

    def estimate_filter_concat_name(self) -> str:
        estimate_filter_names = sorted([e.estimate_filter_name for e in self.estimated_list])
        return "_".join(estimate_filter_names)

    def visualize(self, method: Method, size_ratio: int = 2) -> StockDataVisualized:
        df = self.stock.to_df()
        processed_df = method.process_method.process(df=df)
        if method.visualize_method:
            return method.visualize_method.visualize(size_ratio=size_ratio, df=processed_df.df)
        else:
            raise KabutobashiEntityError(f"method {method.process_method.method_name} has no visualize method")

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.stock.brand.name,
            "market": self.stock.brand.market,
            "industry_type": self.stock.brand.industry_type,
            "weighted_estimated_value": self.weighted_estimated_value(),
            "estimate_name": self.estimate_filter_concat_name(),
        }

    @staticmethod
    def from_dict(data: dict):
        raise NotImplementedError("The method would not be implemented.")
