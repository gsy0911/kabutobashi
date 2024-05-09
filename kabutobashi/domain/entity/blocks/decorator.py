from types import FunctionType

import pandas as pd

from .abc_block import BlockGlue

__all__ = ["block"]

blocks_dict = {}


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
    res = self._process()
    if type(res) is tuple:
        if len(res) == 2:
            if type(res[0]) is dict and type(res[1]) is pd.DataFrame:
                return BlockGlue(series=res[1], params=res[0], block_outputs={})
            elif type(res[1]) is dict and type(res[0]) is pd.DataFrame:
                return BlockGlue(series=res[0], params=res[1], block_outputs={})
            else:
                raise ValueError()
        else:
            raise ValueError()
    elif type(res) is dict:
        return BlockGlue(series=None, params=res, block_outputs={})
    elif type(res) is pd.DataFrame:
        return BlockGlue(series=res, params=None, block_outputs={})
    else:
        raise ValueError()


def _inner_class_func_factory(cls, glue: BlockGlue):
    return cls._factory(glue)


def _inner_class_func_operate(cls, glue: BlockGlue) -> BlockGlue:
    instance = cls._factory(glue)
    new_glue = instance.process()
    return new_glue


def _process_class(cls, block_name: str = None):
    cls_params = {}
    cls_annotations = cls.__dict__.get("__annotations__", {})
    for name, type_ in cls_annotations.items():
        print(f"{name=}, {type_=}")
    print("==============")

    cls_keys = cls.__dict__.keys()
    if "_process" not in cls_keys:
        raise KeyError()
    if "_factory" not in cls_keys:
        raise KeyError()
    if not isinstance((cls.__dict__["_process"]), FunctionType):
        raise ValueError()
    if not type(cls.__dict__["_factory"]) is classmethod:
        raise ValueError()

    for name, value in cls.__dict__.items():
        if name in cls_annotations:
            #     raise TypeError(f'{name} is a field but has no type annotation')
            cls_params[name] = value

            print(f"{name=}, {value=}")

    # set-block-name
    setattr(cls, "block_name", block_name)
    # set-params
    setattr(cls, "params", cls_params)
    # process function
    _set_new_attribute(cls=cls, name="process", value=_inner_func_process)
    # factory function
    _set_new_attribute(cls=cls, name="factory", value=classmethod(_inner_class_func_factory))
    # operate function
    _set_new_attribute(cls=cls, name="operate", value=classmethod(_inner_class_func_operate))
    # validation functions
    _set_new_attribute(cls=cls, name="validate_block_input", value=_inner_func_process)
    _set_new_attribute(cls=cls, name="validate_block_output", value=_inner_func_process)

    blocks_dict.update({block_name: cls})
    return cls


def block(cls=None, /, *, block_name: str = None):
    def wrap(_cls):
        return _process_class(_cls, block_name=block_name)

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        # We're called with parens.
        return wrap
    return wrap(cls)
