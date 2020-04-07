import pandas as pd


class StockDf(object):
    """
    様々な値の保持に用いるクラス。
    値を代入する際にバリデーションが行われる。
    """
    def __init__(self):
        """
        """
        self.name = None
        self.internal_name = None

    def __get__(self, instance, instance_type):
        return getattr(instance, self.internal_name, None)

    def __set__(self, instance, value):
        if value is None:
            raise ValueError("required")

        df_columns = value.columns
        if "code" in df_columns:
            code = list(set(value.code.values))
            if len(code) > 1:
                raise ValueError("multiple code")
            elif len(code) == 0:
                raise ValueError("no code")

        # indexにdateを指定
        value.index = pd.to_datetime(value['date'])
        # 必要なカラムに絞る
        value = value.loc[:, ["open", "high", "low", "close"]]
        # 型の指定
        value['open'] = value['open'].astype(float)
        value['close'] = value['close'].astype(float)
        value['high'] = value['high'].astype(float)
        value['low'] = value['low'].astype(float)
        setattr(instance, self.internal_name, value)
