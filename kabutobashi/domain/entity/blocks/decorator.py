import re
import warnings
from dataclasses import dataclass
from types import FunctionType
from typing import Iterator, Optional, Tuple, Union

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockDecoratorNameError

from .abc_block import BlockGlue

__all__ = ["block"]

blocks_dict = {}


@dataclass(frozen=True)
class BlockInput:
    series: pd.DataFrame
    params: dict


@dataclass(frozen=True)
class BlockOutput:
    series: Optional[pd.DataFrame]
    params: Optional[dict]
    block_name: str


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


def _inner_func_process(self) -> BlockGlue:
    """
    The method is NOT intended to override by users.

    Returns:
        BlockGlue
    """
    res: Union[dict, pd.DataFrame, Tuple[dict, pd.DataFrame], Tuple[pd.DataFrame, dict]] = self._process()
    block_name = self.block_name
    res_glue = BlockGlue()
    if self._glue:
        res_glue = self._glue

    if type(res) is tuple:
        if len(res) == 2:
            if type(res[0]) is dict and type(res[1]) is pd.DataFrame:
                block_output = BlockOutput(series=res[1], params=res[0], block_name=block_name)
            elif type(res[1]) is dict and type(res[0]) is pd.DataFrame:
                block_output = BlockOutput(series=res[0], params=res[1], block_name=block_name)
            else:
                raise ValueError()
        else:
            raise ValueError()
    elif type(res) is dict:
        block_output = BlockOutput(series=None, params=res, block_name=block_name)
    elif type(res) is pd.DataFrame:
        block_output = BlockOutput(series=res, params=None, block_name=block_name)
    else:
        raise ValueError()
    return BlockGlue(series=res_glue.series, params=res_glue.series, block_outputs={block_name: block_output})


def _inner_class_func_factory(cls, glue: BlockGlue):
    """
    The method is NOT intended to override by users.

    Returns:
        cls()
    """
    setattr(cls, "_glue", glue)
    # to set parameters to cls() from glue.params
    block_name = cls().block_name
    params = glue.params.get(block_name, {})
    for k, v in params.items():
        setattr(cls, k, v)
    return cls._factory(glue)


def _inner_class_default_private_func_factory(cls, glue: BlockGlue):
    """
    Default _factory() method.
    The method is intended to override by users.

    Returns:
        cls()
    """
    return cls(series=glue.series, params=glue.params)


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


def _process_class(cls, block_name: str, pre_condition_block_name: str, factory: bool, process: bool):
    cls_params = {}
    cls_annotations = cls.__dict__.get("__annotations__", {})
    if not cls.__name__.endswith("Block"):
        raise KabutobashiBlockDecoratorNameError(f"class name must end with 'Block', {cls.__name__} is not allowed.")

    cls_keys = cls.__dict__.keys()
    # check _process
    if process:
        if "_process" not in cls_keys:
            raise KeyError()
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
            raise KeyError()
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
    _set_new_attribute(cls=cls, name="validate_block_input", value=_inner_func_process)
    _set_new_attribute(cls=cls, name="validate_block_output", value=_inner_func_process)
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
    pre_condition_block_name: str = None,
    factory: bool = False,
    process: bool = True,
):
    """

    Args:
        cls: class to decorate
        block_name: BlockName
        pre_condition_block_name:
        factory: True if _factory() method is required to implement.
        process: True if _process() method is required to implement.

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
        return _process_class(
            _cls,
            block_name=block_name,
            pre_condition_block_name=pre_condition_block_name,
            factory=factory,
            process=process,
        )

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        # We're called with parens.
        return wrap
    return wrap(cls)
