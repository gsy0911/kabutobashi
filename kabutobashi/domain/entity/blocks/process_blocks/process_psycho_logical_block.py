from dataclasses import dataclass

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue
from ..decorator import block
from .abc_process_block import IProcessBlockInput


@dataclass(frozen=True)
class ProcessPsychoLogicalBlockInput(IProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        input_params = block_glue.params.get("process_macd", {})
        psycho_term = input_params.get("psycho_term", 12)
        upper_threshold = input_params.get("upper_threshold", 0.75)
        lower_threshold = input_params.get("lower_threshold", 0.25)
        return cls(
            series=block_glue.series,
            params={
                "psycho_term": psycho_term,
                "upper_threshold": upper_threshold,
                "lower_threshold": lower_threshold,
            },
        )

    def _validate(self):
        pass


@block(block_name="process_psycho_logical", pre_condition_block_name="read_example")
class ProcessPsychoLogicalBlock:
    series: pd.DataFrame
    psycho_term: int = 12
    upper_threshold: float = 0.75
    lower_threshold: float = 0.25

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        df_ = df.copy()
        df_["shift_close"] = df_["close"].shift(1)
        df_ = df_.fillna(0)
        df_["diff"] = df_.apply(lambda x: x["close"] - x["shift_close"], axis=1)

        df_["is_raise"] = df_["diff"].apply(lambda x: 1 if x > 0 else 0)

        df_["psycho_sum"] = df_["is_raise"].rolling(self.psycho_term).sum()
        df_["psycho_line"] = df_["psycho_sum"].apply(lambda x: x / self.psycho_term)

        df_["bought_too_much"] = df_["psycho_line"].apply(lambda x: 1 if x > self.upper_threshold else 0)
        df_["sold_too_much"] = df_["psycho_line"].apply(lambda x: 1 if x < self.lower_threshold else 0)
        return df_

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df["buy_signal"] = df["sold_too_much"]
        df["sell_signal"] = df["bought_too_much"]
        return df

    def _process(self) -> pd.DataFrame:

        applied_df = self._apply(df=self.series)
        signal_df = self._signal(df=applied_df)
        required_columns = ["psycho_line", "bought_too_much", "sold_too_much", "buy_signal", "sell_signal"]
        return signal_df[required_columns]
