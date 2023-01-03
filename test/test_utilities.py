import pytest

import kabutobashi as kb
from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.utilities import convert_float, convert_int, replace


def test_workday():
    date_list = kb.get_past_n_days("2020-03-31", 30)
    assert len(date_list) == 30
    # 祝日が除かれていることを確認
    assert "2020-03-20" not in date_list
    # 土日が除かれていることを確認
    assert "2020-03-07" not in date_list
    assert "2020-03-08" not in date_list
    assert "2020-03-14" not in date_list
    assert "2020-03-15" not in date_list
    assert "2020-03-21" not in date_list
    assert "2020-03-22" not in date_list
    assert "2020-03-28" not in date_list
    assert "2020-03-29" not in date_list


def test_replace():
    assert replace("-") == "0"
    assert replace("") == "0"
    assert replace("---") == "0"
    assert replace("1,000") == "1000"
    assert replace("1000円") == "1000"
    assert replace("1000株") == "1000"
    assert replace("1000倍") == "1000"
    assert replace("1,000倍株円") == "1000"


def test_convert_int():
    # pass
    assert convert_int("-") == 0
    assert convert_int("") == 0
    assert convert_int("---") == 0
    assert convert_int("1,000") == 1000
    assert convert_int("1000円") == 1000
    assert convert_int("1000株") == 1000
    assert convert_int("1000倍") == 1000
    assert convert_int("1,000倍株円") == 1000
    assert type(convert_int(float(0))) is int
    assert convert_int(float(0)) == 0

    # error
    with pytest.raises(KabutobashiEntityError):
        convert_int(input_value={})

    with pytest.raises(KabutobashiEntityError):
        convert_int(input_value="a")


def test_convert_float():
    with pytest.raises(KabutobashiEntityError):
        convert_float(input_value={})

    with pytest.raises(KabutobashiEntityError):
        convert_float(input_value="a")
