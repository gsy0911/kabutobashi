import pytest
import pandas as pd
from kabutobashi.attributes import (
    Field,
    StockDf,
    PageContent
)
from kabutobashi.errors import StockDfError


# Fieldクラスを検証するためのscript
class MetaAttribute(type):
    """
    値のget, setに関するメタクラス
    """
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.name = key
                value.internal_name = '_' + key
            elif isinstance(value, StockDf):
                value.name = key
                value.internal_name = '_' + key
            elif isinstance(value, PageContent):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls


class AbstractAttribute(object, metaclass=MetaAttribute):
    pass


class AttributeInstance(AbstractAttribute):
    # Field
    param_int = Field(required_type=int)
    param_str = Field(required_type=str)
    param_required = Field(required=True)
    param_candidate = Field(value_candidate=["one", "two"])
    # StockDf
    stock_df = StockDf()
    # PageContent
    page_content = PageContent()


def test_field_instance():
    fi = AttributeInstance()
    # 値をセットする前に取得した場合はNone
    assert fi.param_required is None
    with pytest.raises(ValueError):
        fi.param_required = None
    # Noneの代入は通る
    fi.param_int = None
    with pytest.raises(ValueError):
        fi.param_candidate = "three"
    with pytest.raises(TypeError):
        fi.param_int = "str"
    with pytest.raises(TypeError):
        fi.param_str = 0


def test_stock_df_instance():
    fi = AttributeInstance()
    # 値をセットする前に取得した場合はNone
    assert fi.stock_df is None
    with pytest.raises(StockDfError):
        fi.stock_df = None

    # カンマを含むデータを入れても正しく動くか確認
    data = {
        0: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-01"},
        1: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-02"},
        2: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-03"},
        3: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-04"},
        4: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-05"},
    }
    fi.stock_df = pd.DataFrame.from_dict(data, orient="index")
    columns = fi.stock_df.columns
    assert "open" in columns
    assert "high" in columns
    assert "low" in columns
    assert "close" in columns

    # 日付の項目がdtでも動くかの確認
    data = {
        0: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "dt": "2020-03-01"},
        1: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "dt": "2020-03-02"},
        2: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "dt": "2020-03-03"},
        3: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "dt": "2020-03-04"},
        4: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "dt": "2020-03-05"},
    }
    fi.stock_df = pd.DataFrame.from_dict(data, orient="index")
    columns = fi.stock_df.columns
    assert "open" in columns
    assert "high" in columns
    assert "low" in columns
    assert "close" in columns

    # date列がない場合にErrorを返す
    data = {
        0: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0"},
        1: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0"},
        2: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0"},
        3: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0"},
        4: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0"},
    }
    with pytest.raises(StockDfError):
        fi.stock_df = pd.DataFrame.from_dict(data, orient="index")

    # 日付の項目がdtでも動くかの確認
    data = {
        0: {"open": "1.0", "high": "2.0", "low": "3.0", "close": "4.0", "dt": "2020-03-01", "date": "2020-03-01"},
        1: {"open": "1.0", "high": "2.0", "low": "3.0", "close": "4.0", "dt": "2020-03-02", "date": "2020-03-02"},
        2: {"open": "1.0", "high": "2.0", "low": "3.0", "close": "4.0", "dt": "2020-03-03", "date": "2020-03-03"},
        3: {"open": "1.0", "high": "2.0", "low": "3.0", "close": "4.0", "dt": "2020-03-04", "date": "2020-03-04"},
        4: {"open": "1.0", "high": "2.0", "low": "3.0", "close": "4.0", "dt": "2020-03-05", "date": "2020-03-05"},
    }
    with pytest.raises(StockDfError):
        fi.stock_df = pd.DataFrame.from_dict(data, orient="index")

    # valueにfloatに変換できな文字列が含まれている場合にエラーを返すテスト
    data = {
        0: {"open": "-------", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-01"},
        1: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-02"},
        2: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-03"},
        3: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-04"},
        4: {"open": "1,000.0", "high": "2,000.0", "low": "3,000.0", "close": "4,000.0", "date": "2020-03-05"},
    }
    with pytest.raises(StockDfError):
        fi.stock_df = pd.DataFrame.from_dict(data, orient="index")


def test_page_content_instance():
    fi = AttributeInstance()
    # 値をセットする前に取得した場合はNone
    assert fi.page_content is None
    with pytest.raises(ValueError):
        fi.page_content = None
