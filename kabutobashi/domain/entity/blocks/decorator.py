import re
import warnings
from dataclasses import dataclass
from functools import partial
from inspect import signature
from logging import getLogger
from types import FunctionType
from typing import Iterator, List, NoReturn, Optional, Tuple, TypeAlias, Union

import pandas as pd

from kabutobashi.domain.errors import (
    KabutobashiBlockDecoratorNameError,
    KabutobashiBlockDecoratorNotImplementedError,
    KabutobashiBlockDecoratorReturnError,
    KabutobashiBlockDecoratorTypeError,
)

from .basis_blocks import BlockGlue, BlockOutput, SeriesRequiredColumnsMode

__all__ = ["block", "block_from"]

blocks_dict = {}
logger = getLogger(__name__)

# type candidates of `UdfBlock._process()` return
BlockProcessResultType: TypeAlias = Union[dict, pd.DataFrame, Tuple[dict, pd.DataFrame], Tuple[pd.DataFrame, dict]]


@dataclass(frozen=True)
class SeriesRequiredColumn:
    block_name: str
    keys: List[str]
    priority: int


@dataclass(frozen=True)
class ParamsRequiredKey:
    block_name: str
    keys: List[str]
    priority: int


def _to_snake_case(string: str) -> str:
    # see: https://qiita.com/munepi0713/items/82ce7a56aa1b8233fd30
    _PARSE_BY_SEP_PATTERN = re.compile(r"[ _-]+")
    _PARSE_PATTERN = re.compile(r"[A-Za-z][^A-Z]+")

    def _parse_words(_string: str) -> Iterator[str]:
        for block in re.split(_PARSE_BY_SEP_PATTERN, _string):
            for m in re.finditer(_PARSE_PATTERN, block):
                yield m.group(0)

    word_iter = _parse_words(string)
    return "_".join(word.lower() for word in word_iter)


def _set_qualname(cls, value):
    # Ensure that the functions returned from _create_fn uses the proper
    # __qualname__ (the class they belong to).
    if isinstance(value, FunctionType):
        value.__qualname__ = f"{cls.__qualname__}.{value.__name__}"
    return value


def _set_new_attribute(cls, name, value):
    # Never overwrites an existing attribute.  Returns True if the
    # attribute already exists.
    if name in cls.__dict__:
        return True
    _set_qualname(cls, value)
    setattr(cls, name, value)
    return False


def _inner_func_validate_input(self, *, functions: List[callable] = None) -> NoReturn:
    """
    The method is NOT intended to override by users.
    """
    logger.debug(f"{self.params=}")
    for f in functions:
        sig = signature(f)
        function_required_args = sig.parameters.keys()
        function_args = {k: v for k, v in self.__dict__.items() if (k in function_required_args)}
        logger.debug(f"{f} <= {function_args=}")
        f(self, **function_args)


def _inner_func_validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]) -> NoReturn:
    """
    The method is NOT intended to override by users.
    """
    self._validate_output(series=series, params=params)


def _inner_func_private_validate_output(self, series: Optional[pd.DataFrame], params: Optional[dict]) -> NoReturn:
    """
    Default _validate_output() method.
    The method is intended to override by users.
    """
    pass


def _inner_func_process(self) -> BlockGlue:
    """
    The method is NOT intended to override by users.
    The method can be called by `cls.process()`

    Returns:
        BlockGlue
    """
    # initialize
    block_name = self.block_name
    res_glue = BlockGlue()
    if self._glue:
        res_glue = self._glue
    # validate_input
    self.validate_input()
    # process()
    res: BlockProcessResultType = self._process()
    execution_order = res_glue.get_max_execution_order() + 1

    if type(res) is tuple:
        if len(res) == 2:
            if type(res[0]) is dict and type(res[1]) is pd.DataFrame:
                self.validate_output(series=res[1], params=res[0])
                block_output = BlockOutput(
                    series=res[1], params=res[0], block_name=block_name, execution_order=execution_order
                )
            elif type(res[1]) is dict and type(res[0]) is pd.DataFrame:
                self.validate_output(series=res[0], params=res[1])
                block_output = BlockOutput(
                    series=res[0], params=res[1], block_name=block_name, execution_order=execution_order
                )
            else:
                raise KabutobashiBlockDecoratorReturnError(
                    "The return values are limited to combinations of `dict` and `pd.DataFrame`."
                )
        else:
            raise KabutobashiBlockDecoratorReturnError("Please limit the number of return values to two or fewer.")
    elif type(res) is dict:
        self.validate_output(series=None, params=res)
        block_output = BlockOutput(series=None, params=res, block_name=block_name, execution_order=execution_order)
    elif type(res) is pd.DataFrame:
        self.validate_output(series=res, params=None)
        block_output = BlockOutput(series=res, params=None, block_name=block_name, execution_order=execution_order)
    else:
        raise KabutobashiBlockDecoratorReturnError(f"An unexpected return type {type(res)} was returned.")
    block_outputs = res_glue.block_outputs if res_glue.block_outputs else {}
    block_outputs.update({block_name: block_output})
    return BlockGlue(
        series=res_glue.series,
        params=res_glue.params,
        block_outputs=block_outputs,
        execution_order=res_glue.execution_order + 1,
    )


def _inner_class_func_factory(cls, glue: BlockGlue):
    """
    The method is NOT intended to override by users.
    The method can be called by `cls.factory()`

    Returns:
        cls()
    """
    setattr(cls, "_glue", glue)
    # get parameters from glue
    params = {}
    series = None

    res = cls._factory(glue)
    if type(res) is tuple:
        if len(res) == 2:
            if type(res[0]) is dict:
                params, series = res
            elif type(res[1]) is dict:
                series, params = res
            else:
                raise KabutobashiBlockDecoratorReturnError(
                    "The return values are limited to combinations of `dict` and `pd.DataFrame`."
                )
        else:
            raise KabutobashiBlockDecoratorReturnError("Please limit the number of return values to two or fewer.")
    elif type(res) is dict:
        params = res
    elif type(res) is pd.DataFrame:
        series = res
    else:
        raise KabutobashiBlockDecoratorReturnError(f"An unexpected return type {type(res)} was returned.")

    # set attributes
    logger.debug(f"@block._factory(): {cls.__name__}: {params.keys()}")
    for k, v in params.items():
        setattr(cls, k, v)
    return cls(series=series, params=params)


def _inner_class_default_private_func_factory(cls, glue: BlockGlue) -> Tuple[pd.DataFrame, dict]:
    """
    Default _factory() method.
    Although the method is intended to override by users, usually the method is not overridden.
    The method can be called by `cls._factory()`

    Returns:
        cls()
    """
    cls_instance = cls()
    block_name = cls_instance.block_name
    series_required_columns = cls_instance.series_required_columns
    params_required_keys = cls_instance.params_required_keys
    series_required_columns_mode = cls_instance.series_required_columns_mode

    # params
    params = glue.get_params(
        block_name=block_name,
        params_required_keys=params_required_keys,
    )

    # series
    series = glue.get_series(
        series_required_columns=series_required_columns,
        series_required_columns_mode=series_required_columns_mode,
    )
    return series, params


def _inner_class_func_glue(cls, glue: BlockGlue) -> BlockGlue:
    """
    The method is NOT intended to override by users.

    Returns:
        BlockGlue()
    """
    block_instance = cls.factory(glue=glue)
    new_glue = block_instance.process()
    return new_glue


def _inner_init(self, series: Optional[pd.DataFrame] = None, params: Optional[dict] = None):
    """
    The method is NOT intended to override by users.
    """
    self.series = series
    self.params = params


def _inner_repr(self):
    """
    The method is NOT intended to override by users.
    """
    # block name
    repr = ["# block_name: {self.block_name}"]
    # attributes
    repr.extend([f"+ {name}: {value}" for name, value in self.__dict__.items()])
    # repr.extend([f"+ {name}: {getattr(self, name)}" for name in self.__annotations__.keys()])

    return "\n".join(repr)


def _process_class(
    cls,
    block_name: str,
    factory: bool,
    process: bool,
    series_required_columns: List[str | SeriesRequiredColumn],
    series_required_columns_mode: SeriesRequiredColumnsMode,
    params_required_keys: List[str | ParamsRequiredKey],
):
    cls_params = {}
    cls_annotations = cls.__dict__.get("__annotations__", {})
    logger.debug(f"{cls_annotations=}")
    if not cls.__name__.endswith("Block"):
        raise KabutobashiBlockDecoratorNameError(f"class name must end with 'Block', {cls.__name__} is not allowed.")

    cls_keys = cls.__dict__.keys()
    # check _process
    if process:
        if "_process" not in cls_keys:
            raise KabutobashiBlockDecoratorNotImplementedError("_process method is not implemented.")
        if not isinstance((cls.__dict__["_process"]), FunctionType):
            raise ValueError()
        _process_annotation_candidates = [Tuple[dict, pd.DataFrame], Tuple[pd.DataFrame, dict], dict, pd.DataFrame]
        # check annotation types
        _process_annotations = cls.__dict__["_process"].__annotations__
        if "return" in _process_annotations:
            if not any([_process_annotations["return"] is t for t in _process_annotation_candidates]):
                warn_msg = f"{_process_annotations['return']} is not compatible. Use `dict`, `pd.DataFrame`, or `Tuple[dict, pd.DataFrame]`"
                warnings.warn(warn_msg, category=SyntaxWarning)

    # check _factory
    if factory:
        if "_factory" not in cls_keys:
            raise KabutobashiBlockDecoratorNotImplementedError("_factory method is not implemented.")
        if not type(cls.__dict__["_factory"]) is classmethod:
            raise ValueError()

    for name in cls_annotations:
        if name in cls.__dict__.keys():
            cls_params[name] = cls.__dict__[name]
        else:
            cls_params[name] = None

    # set-block-name
    if block_name is None:
        block_name = _to_snake_case(cls.__name__)
    setattr(cls, "block_name", block_name)
    setattr(cls, "series_required_columns", series_required_columns)
    setattr(cls, "params_required_keys", params_required_keys)
    setattr(cls, "series_required_columns_mode", series_required_columns_mode)
    # set-params
    setattr(cls, "params", cls_params)
    # process function
    _set_new_attribute(cls=cls, name="process", value=_inner_func_process)
    # factory function
    _set_new_attribute(cls=cls, name="factory", value=classmethod(_inner_class_func_factory))
    if not factory:
        _set_new_attribute(cls=cls, name="_factory", value=classmethod(_inner_class_default_private_func_factory))
    # operate function
    _set_new_attribute(cls=cls, name="glue", value=classmethod(_inner_class_func_glue))
    # validation functions
    _inner_func_validate_input_partial = partial(
        _inner_func_validate_input,
        self=cls,
        functions=[
            v for k, v in cls.__dict__.items() if k.startswith("_validate") and not k.startswith("_validate_output")
        ],
    )
    _set_new_attribute(cls=cls, name="validate_input", value=_inner_func_validate_input_partial)
    _set_new_attribute(cls=cls, name="validate_output", value=_inner_func_validate_output)
    if "_validate_output" not in cls.__dict__:
        _set_new_attribute(cls=cls, name="_validate_output", value=_inner_func_private_validate_output)
    # dunder-method
    _set_new_attribute(cls=cls, name="__init__", value=_inner_init)
    _set_new_attribute(cls=cls, name="__repr__", value=_inner_repr)
    # register global dict
    blocks_dict.update({block_name: cls})
    return cls


def block(
    cls=None,
    /,
    *,
    block_name: str = None,
    factory: bool = False,
    process: bool = True,
    series_required_columns: List[str | SeriesRequiredColumn] = None,
    series_required_columns_mode: SeriesRequiredColumnsMode = "strict",
    params_required_keys: List[str | ParamsRequiredKey] = None,
):
    """

    Args:
        cls: class to decorate
        block_name: BlockName
        factory: True if _factory() method is required to implement.
        process: True if _process() method is required to implement.
        series_required_columns:
        series_required_columns_mode:
        params_required_keys:

    Returns:
        decorator

    Examples:
        >>> # basic example
        >>> from kabutobashi.domain.entity.blocks import BlockGlue
        >>> @block()
        >>> class SampleBlock:
        >>>     term: int = 10
        >>>
        >>>     @classmethod
        >>>     def _factory(cls, glue: BlockGlue) -> "SampleBlock":
        >>>         return SampleBlock()
        >>>
        >>>     def _process(self):
        >>>         params = self
        >>>         return SampleBlock()
    """

    def wrap(_cls):
        if type(_cls) is not type:
            raise KabutobashiBlockDecoratorTypeError(f"first argument of @block must be a class, not a {type(_cls)}")
        return _process_class(
            _cls,
            block_name=block_name,
            factory=factory,
            process=process,
            series_required_columns=series_required_columns,
            series_required_columns_mode=series_required_columns_mode,
            params_required_keys=params_required_keys,
        )

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        # We're called with parens.
        return wrap
    return wrap(cls)


def block_from(key: str):
    return blocks_dict[key]
