from typing import Union

from kabutobashi.domain.errors import KabutobashiEntityError


def _replace(input_value: str) -> str:
    if input_value == "-":
        return "0"
    return input_value.replace("---", "0").replace("円", "").replace("株", "").replace("倍", "").replace(",", "")


def _convert_float(input_value: Union[str, float, int]) -> float:
    if type(input_value) is float:
        return input_value
    elif type(input_value) is int:
        return float(input_value)
    elif type(input_value) is str:
        try:
            return float(_replace(input_value=input_value))
        except ValueError as e:
            raise KabutobashiEntityError(f"cannot convert {input_value} to float: {e}")
    raise KabutobashiEntityError(f"cannot convert {input_value} to float")


def _convert_int(input_value: Union[str, float, int]) -> int:
    if type(input_value) == int:
        return input_value
    elif type(input_value) == float:
        try:
            return int(input_value)
        except ValueError:
            return 0
    elif type(input_value) is str:
        try:
            return int(_replace(input_value=input_value))
        except ValueError as e:
            raise KabutobashiEntityError(f"cannot convert {input_value} to integer: {e}")
    raise KabutobashiEntityError(f"cannot convert {input_value} to int")
