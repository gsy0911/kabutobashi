import pytest
from pystock.attributes.attribute import (
    Field,
    StockDf,
    PageContent
)


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
    with pytest.raises(ValueError):
        fi.stock_df = None


def test_page_content_instance():
    fi = AttributeInstance()
    # 値をセットする前に取得した場合はNone
    assert fi.page_content is None
    with pytest.raises(ValueError):
        fi.page_content = None
