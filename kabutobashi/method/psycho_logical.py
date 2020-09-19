import pandas as pd
from kabutobashi.method.method import Method
from kabutobashi.attributes import Field


class PsychoLogical(Method):
    """
    See Also:
        https://www.sevendata.co.jp/shihyou/technical/psycho.html
    """
    upper_threshold = Field(required_type=float)
    lower_threshold = Field(required_type=float)
    psycho_term = Field(required_type=int)

    def __init__(
            self,
            upper_threshold=0.75,
            lower_threshold=0.25,
            psycho_term=12):
        super().__init__(method_name="psycho_logical")
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.psycho_term = psycho_term

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df['shift_close'] = _df['close'].shift(1)
        _df['diff'] = _df.apply(lambda x: x['close']-x['shift_close'], axis=1)
        
        _df['is_raise'] = _df['diff'].apply(lambda x: 1 if x > 0 else 0)
        
        _df['psycho_sum'] = _df['is_raise'].rolling(self.psycho_term).sum()
        _df['psycho_line'] = _df['psycho_sum'].apply(lambda x: x/self.psycho_term)
        
        _df['bought_too_much'] = _df['psycho_line'].apply(lambda x: 1 if x > self.upper_threshold else 0)
        _df['sold_too_much'] = _df['psycho_line'].apply(lambda x: 1 if x < self.lower_threshold else 0)
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df['buy_signal'] = _df['sold_too_much']
        _df['sell_signal'] = _df['bought_too_much']
        return _df
