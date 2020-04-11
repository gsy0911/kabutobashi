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

        open_s = value['open'].apply(self._replace_comma)
        close_s = value['close'].apply(self._replace_comma)
        high_s = value['high'].apply(self._replace_comma)
        low_s = value['low'].apply(self._replace_comma)
        new_value = pd.DataFrame({"open": open_s, "high": high_s, "low": low_s, "close": close_s})
        # 型の指定
        setattr(instance, self.internal_name, new_value)

    @staticmethod
    def _replace_comma(x) -> float:
        """
        pandas内の値がカンマ付きの場合に、カンマを削除する関数
        :param x:
        :return:
        """
        if type(x) is str:
            x = x.replace(",", "")
        return float(x)
