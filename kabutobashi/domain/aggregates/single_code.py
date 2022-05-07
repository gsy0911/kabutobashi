from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, Generator, List, Optional, Tuple, Union

import pandas as pd

from kabutobashi.domain.entity.stock_data_estimated import StockDataEstimatedBySingleFilter
from kabutobashi.domain.entity.stock_data_processed import StockDataProcessedBySingleMethod
from kabutobashi.domain.entity.stock_data_raw import StockDataSingleCode
from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.services.estimate_filter import EstimateFilter
from kabutobashi.domain.services.method import Method

__all__ = ["StockCodeSingleAggregate"]


@dataclass(frozen=True)
class StockCodeSingleAggregate:
    code: str
    single_code: StockDataSingleCode
    processed_list: List[StockDataProcessedBySingleMethod] = field(default_factory=list, repr=False)
    estimated_list: List[StockDataEstimatedBySingleFilter] = field(default_factory=list, repr=False)

    @staticmethod
    def of(df: pd.DataFrame) -> "StockCodeSingleAggregate":
        single_code = StockDataSingleCode.of(df=df)
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
