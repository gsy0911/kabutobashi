from dataclasses import dataclass, field, replace
from logging import getLogger
from typing import Dict, List, Literal, Optional, TypeAlias, Union

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockGlueError

logger = getLogger(__name__)

__all__ = ["BlockGlue", "BlockOutput", "SeriesRequiredColumnsMode"]
SeriesRequiredColumnsMode: TypeAlias = Literal["strict", "all"]


@dataclass(frozen=True)
class BlockInput:
    series: pd.DataFrame
    params: dict


@dataclass(frozen=True)
class BlockOutput:
    series: Optional[pd.DataFrame]
    params: Optional[dict]
    block_name: str
    execution_order: int = 1


@dataclass(frozen=True)
class IBlock:
    pass


@dataclass(frozen=True)
class SeriesColumns:
    block_name: str
    columns: List[str]
    execution_order: int

    def __lt__(self, other: "SeriesColumns") -> bool:
        if not isinstance(other, SeriesColumns):
            raise ValueError
        return self.execution_order > other.execution_order

    @staticmethod
    def fix(series_columns_list: List["SeriesColumns"]) -> List["SeriesColumns"]:
        res_list = []
        _existed_columns = []
        sorted_list = sorted(series_columns_list)
        for sc in sorted_list:
            unique_elements = list(set(sc.columns).symmetric_difference(set(_existed_columns)) & set(sc.columns))
            _existed_columns.extend(sc.columns)
            res_list.append(replace(sc, columns=unique_elements))
        return res_list


@dataclass(frozen=True)
class BlockGlue:
    series: Optional[pd.DataFrame] = None
    params: Optional[dict] = None
    block_outputs: Dict[str, BlockOutput] = field(default_factory=dict, repr=False)
    execution_order: int = 1

    def update(self, block_output: BlockOutput) -> "BlockGlue":
        self.block_outputs[block_output.block_name] = block_output
        if self.series is None:
            series = block_output.series
        else:
            series = self.series

        if self.params is None:
            params = block_output.params
        else:
            params = self.params
        return replace(self, series=series, params=params, block_outputs=self.block_outputs)

    def get_series_from_required_columns(
        self, required_columns: List[str], series_required_columns_mode: SeriesRequiredColumnsMode = "strict"
    ) -> pd.DataFrame:
        logger.debug(f"{required_columns=}")
        orders = [v.execution_order for _, v in self if v.series is not None]
        if len(orders) != len(set(orders)):
            raise KabutobashiBlockGlueError(f"{orders=} must be unique.")
        series_columns_list = [
            SeriesColumns(block_name=v.block_name, columns=v.series.columns, execution_order=v.execution_order)
            for _, v in self
            if v.series is not None
        ]
        fixed_series_columns_list = SeriesColumns.fix(series_columns_list=series_columns_list)
        initial_series = self[fixed_series_columns_list[0].block_name].series[fixed_series_columns_list[0].columns]
        rest_series = [self[v.block_name].series[v.columns] for v in fixed_series_columns_list[1:]]
        series = initial_series.join(rest_series)
        if series_required_columns_mode == "strict":
            return series[required_columns]
        elif series_required_columns_mode == "all":
            return series
        else:
            raise ValueError()

    def get_series(
        self,
        pre_condition_block_name: str,
        series_required_columns: Optional[list],
        series_required_columns_mode: SeriesRequiredColumnsMode,
    ) -> Optional[pd.DataFrame]:
        if self.series is not None:
            series = self.series
        elif series_required_columns is not None and type(series_required_columns) is list:
            series = self.get_series_from_required_columns(
                required_columns=series_required_columns, series_required_columns_mode=series_required_columns_mode
            )
        elif self.block_outputs is not None:
            series = self.block_outputs.get(pre_condition_block_name, None)
            if series is not None:
                series = series.series
        else:
            series = None
        return series

    def get_params(
        self, block_name: str, pre_condition_block_name: Optional[str], params_required_keys: Optional[Union[str, list]]
    ) -> dict:
        params = {}
        if self.params is not None:
            params.update(self.params.get(block_name, {}))
        if pre_condition_block_name is not None:
            block_output: Optional[BlockOutput] = self.block_outputs.get(pre_condition_block_name)
            if block_output is not None:
                if block_output.params is not None:
                    params.update(block_output.params)
        if params_required_keys is not None and type(params_required_keys) is list:
            logger.debug(f"{params_required_keys=}")
            params = {}
            for _, v in self:
                if v.params is None:
                    continue
                params.update(v.params)
        return params

    def get_max_execution_order(self) -> int:
        execution_order = [0]
        execution_order.extend([v.execution_order for _, v in self.block_outputs.items()])
        return max(execution_order)

    def __len__(self):
        return len(self.block_outputs.keys())

    def __getitem__(self, key: str):
        if type(key) is str:
            return self.block_outputs[key]
        else:
            raise KeyError(f"Key {key} is not a str")

    def __iter__(self):
        for k, v in self.block_outputs.items():
            yield k, v

    def __contains__(self, item: str):
        if type(item) is str:
            return item in self.block_outputs.keys()
        else:
            raise KeyError(f"Key {item} is not a str")
