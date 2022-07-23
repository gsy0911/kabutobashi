from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, NoReturn, Optional, Union

import pandas as pd

from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.services.estimate_filter import EstimateFilter
from kabutobashi.domain.services.method import Method
from kabutobashi.domain.values import (
    StockDataEstimatedBySingleFilter,
    StockDataProcessedBySingleMethod,
    StockDataSingleCode,
    StockDataVisualized,
    StockRecordset,
)

__all__ = ["StockCodeSingleAggregate", "IStockCodeSingleAggregateRepository"]


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
        >>> filters = kb.estimate_filters
        >>>
        >>> for df in records.to_code_iterable(until=1, row_more_than=80):
        >>>     agg = kb.StockCodeSingleAggregate.of(entity=df).with_processed(methods).with_estimated(filters)
        >>>     print(agg.weighted_estimated_value())
    """

    code: str
    single_code: StockDataSingleCode
    processed_list: List[StockDataProcessedBySingleMethod] = field(default_factory=list, repr=False)
    estimated_list: List[StockDataEstimatedBySingleFilter] = field(default_factory=list, repr=False)

    @staticmethod
    def of(
        entity: Union[pd.DataFrame, StockDataSingleCode, StockRecordset], *, code: Optional[str] = None
    ) -> "StockCodeSingleAggregate":
        if type(entity) is pd.DataFrame:
            single_code = StockDataSingleCode.of(df=entity)
        elif type(entity) is StockDataSingleCode:
            single_code = entity
        elif type(entity) is StockRecordset:
            if code is None:
                raise KabutobashiEntityError("code is required")
            df_ = entity.to_df(code=code)
            single_code = StockDataSingleCode.of(df=df_)
        else:
            raise KabutobashiEntityError("accept pd.DataFrame or StockDataSingleCode")
        return StockCodeSingleAggregate(code=single_code.code, single_code=single_code)

    def _to_single_processed(self, method: Method) -> StockDataProcessedBySingleMethod:
        df = self.single_code.to_df()
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

    def with_processed(self, methods: List[Method]) -> "StockCodeSingleAggregate":
        # check all methods
        for method in methods:
            if not isinstance(method, Method):
                raise KabutobashiEntityError()

        return StockCodeSingleAggregate(
            code=self.code, single_code=self.single_code, processed_list=[self._to_single_processed(m) for m in methods]
        )

    def _to_single_estimated(self, estimate_filter: EstimateFilter) -> StockDataEstimatedBySingleFilter:
        def get_impacts(influence: int = 2, tail: int = 5) -> Dict[str, float]:
            data_ = {}
            for a in self.processed_list:
                data_.update(a.get_impact(influence=influence, tail=tail))
            return data_

        def get_parameters():
            data_ = {}
            for a in self.processed_list:
                data_.update(a.parameters)
            return data_

        data = {}
        data.update(get_impacts())
        data.update(get_parameters())
        return StockDataEstimatedBySingleFilter(
            code=self.code,
            estimate_filter_name=estimate_filter.estimate_filter_name,
            estimated_value=estimate_filter.estimate(data=data),
        )

    def with_estimated(self, estimate_filters: List[EstimateFilter]) -> "StockCodeSingleAggregate":
        """

        Returns:
            StockDataEstimatedByMultipleFilter
        """
        return StockCodeSingleAggregate(
            code=self.code,
            single_code=self.single_code,
            processed_list=self.processed_list,
            estimated_list=[self._to_single_estimated(estimate_filter=ef) for ef in estimate_filters],
        )

    def weighted_estimated_value(self, weights: dict = None) -> float:
        if not weights:
            weights = {}
        return sum([e.weighted_estimated_value(weights=weights) for e in self.estimated_list])

    def estimate_filter_concat_name(self) -> str:
        estimate_filter_names = sorted([e.estimate_filter_name for e in self.estimated_list])
        return "_".join(estimate_filter_names)

    def visualize(self, size_ratio: int = 2) -> StockDataVisualized:
        if not self.processed_list:
            raise KabutobashiEntityError("call with_processed() before.")
        return StockDataVisualized.of(processed=self.processed_list, size_ratio=size_ratio)


class IStockCodeSingleAggregateRepository(metaclass=ABCMeta):
    def read(self, code: str) -> "StockCodeSingleAggregate":
        return StockCodeSingleAggregate(
            code=code,
            single_code=self._stock_data_read(code=code),
            processed_list=self._stock_processed_read(code=code),
            estimated_list=self._stock_estimated_read(code=code),
        )

    @abstractmethod
    def _stock_data_read(self, code: str) -> "StockDataSingleCode":
        raise NotImplementedError()

    @abstractmethod
    def _stock_processed_read(self, code: str) -> List["StockDataProcessedBySingleMethod"]:
        raise NotImplementedError()

    @abstractmethod
    def _stock_estimated_read(self, code: str) -> List["StockDataEstimatedBySingleFilter"]:
        raise NotImplementedError()

    def write(self, data: StockCodeSingleAggregate) -> NoReturn:
        self._stock_data_write(data=data.single_code)
        self._stock_processed_write(data=data.processed_list)
        self._stock_estimated_write(data=data.estimated_list)

    @abstractmethod
    def _stock_data_write(self, data: StockDataSingleCode) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def _stock_processed_write(self, data: List[StockDataProcessedBySingleMethod]) -> NoReturn:
        raise NotImplementedError()

    @abstractmethod
    def _stock_estimated_write(self, data: List[StockDataEstimatedBySingleFilter]) -> NoReturn:
        raise NotImplementedError()
