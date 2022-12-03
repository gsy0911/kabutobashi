from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, NoReturn, Optional, Union

import pandas as pd

from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.services.analyze import StockAnalysis
from kabutobashi.domain.services.method import Method
from kabutobashi.domain.values import StockDataEstimated, StockDataProcessed, StockDataVisualized, StockRecordset

__all__ = ["StockCodeSingleAggregate", "IStockCodeSingleAggregateReadRepository"]


@dataclass(frozen=True)
class StockCodeSingleAggregate:
    """
    StockCodeSingleAggregate: Aggregate

    Examples:
        >>> import kabutobashi as kb
        >>> import pandas as pd
        >>> data_list = []
        >>> records = kb.example()
        >>> methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
        >>> stock_analysis = kb.stock_analysis
        >>>
        >>> for df in records.to_code_iterable(until=1, row_more_than=80):
        >>>     agg = kb.StockCodeSingleAggregate.of(entity=df).with_processed(methods).with_estimated(stock_analysis)
        >>>     print(agg.weighted_estimated_value())
    """

    code: str
    single_recordset: StockRecordset
    processed_list: List[StockDataProcessed] = field(default_factory=list, repr=False)
    estimated_list: List[StockDataEstimated] = field(default_factory=list, repr=False)

    def __post_init__(self):
        _ = self.single_recordset.get_single_code_recordset_status()

    @staticmethod
    def of(entity: Union[pd.DataFrame, StockRecordset], *, code: Optional[str] = None) -> "StockCodeSingleAggregate":
        if type(entity) is pd.DataFrame:
            single_recordset = StockRecordset.of(df=entity)
        elif type(entity) is StockRecordset:
            if code is None and entity.code_num > 1:
                raise KabutobashiEntityError("code is required")
            df_ = entity.to_df(code=code)
            single_recordset = StockRecordset.of(df=df_)
        else:
            raise KabutobashiEntityError("accept pd.DataFrame or StockDataSingleCode")

        code = single_recordset.get_single_code_recordset_status().code
        return StockCodeSingleAggregate(code=code, single_recordset=single_recordset)

    def with_processed(self, methods: List[Method]) -> "StockCodeSingleAggregate":
        # check all methods
        for method in methods:
            if not isinstance(method, Method):
                raise KabutobashiEntityError()

        df = self.single_recordset.to_df()
        return StockCodeSingleAggregate(
            code=self.code,
            single_recordset=self.single_recordset,
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
            single_recordset=self.single_recordset,
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
        df = self.single_recordset.to_df()
        processed_df = method.process_method.process(df=df)
        if method.visualize_method:
            return method.visualize_method.visualize(size_ratio=size_ratio, df=processed_df.df)
        else:
            raise KabutobashiEntityError(f"method {method.process_method.method_name} has no visualize method")


class IStockCodeSingleAggregateReadRepository(ABC):
    def read(self, code: str) -> "StockCodeSingleAggregate":
        return StockCodeSingleAggregate(
            code=code,
            single_recordset=self._stock_data_read(code=code),
            processed_list=[],
            estimated_list=[],
        )

    @abstractmethod
    def _stock_data_read(self, code: str) -> "StockRecordset":
        raise NotImplementedError()
