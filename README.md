# kabutobashi

[![pytest](https://github.com/gsy0911/kabutobashi/workflows/pytest/badge.svg)](https://github.com/gsy0911/kabutobashi/actions?query=workflow%3Apytest)
[![codecov](https://codecov.io/gh/gsy0911/kabutobashi/branch/main/graph/badge.svg)](https://codecov.io/gh/gsy0911/kabutobashi)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

[![PythonVersion](https://img.shields.io/pypi/pyversions/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![PiPY](https://img.shields.io/pypi/v/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![Documentation Status](https://readthedocs.org/projects/kabutobashi/badge/?version=latest)](https://kabutobashi.readthedocs.io/en/latest/?badge=latest)

# Core Concept

`@block`-decorator and `Flow`-class is important.
`@block` automatically generates input and output functions, allowing you to focus solely on the processing.
`Flow` allows you to focus solely on the process flow and input parameters.

## About `@block`-decorator

simple decorator is like below.

```python
def simple_decorator(func):
    def wrap_func() -> str:
        res = func()
        return f"Hello, {res}"
    return wrap_func


@simple_decorator
def world() -> str:
    return "world"


world()  # => "Hello, world"
```

A `decorator` is something that dynamically generates and adds processes to functions or classes, similar to its name.


First, prepare a function as follows and decorate it with `@block`.

```python
from kabutobashi import block

@block()
class UdfBlock:
    term: int = 10

    def _process(self):
        return {"doubled_term": self.term * 2}
```

The classes above is equivalent to the following class definition.

```python
import pandas as pd
from kabutobashi.domain.entity.blocks import BlockGlue

class UdfBlock:
    series: pd.DataFrame = None
    params: dict = None
    term: int = 10
    block_name: str = "udf_block"

    def _process(self) -> dict:
        return {"doubled_term": self.term * 2}
    
    def process(self) -> BlockGlue:
        # _process() method can be Tuple[Optional[dict], Optional[pd.DataFrame]]
        res = self._process()
        return BlockGlue(params=res, series=None, block_outputs={})

    def factory(self, glue: BlockGlue) -> "UdfBlock":
        # Omitted. In reality, processes are described.
        ...

    def _factory(self, glue: BlockGlue) -> dict:
        # Omitted. In reality, processes are described.
        ...

    def glue(self, glue: BlockGlue) -> BlockGlue:
        # Omitted. In reality, processes are described.
        ...

```

In classes decorated with `@block`, it is not recommended to execute the `__init__()` method. Instead, it is recommended to use the `factory()` class-method.

`factory()` method description.
`process()` method description.
`glue()` method description.

```mermaid
sequenceDiagram
  autonumber
  participant G as glue()
  participant UC as UdfBlock::class
  create participant S1 as factory()
  UC->>S1: create
  create participant S2 as _factory()
  UC->>S2: create or defined by user
  create participant P1 as process()
  UC->>P1: create
  create participant P2 as _process()
  UC->>P2: create or defined by user
  Note over S1: Generate udf_block_instance
  G->>+S1: Request
  S1->>+S2: Request
  Note over S2: User can modify _factory()
  S2-->>S2: get params from glue
  S2-->>S2: get series from glue
  S2-->>-S1: params and series
  create participant UI as UdfBlock::instance
  S1->>UI: UdfBlock(params, series)
  S1->>UI: setattr params to udf_block_instance
  S1-->>-G: udf_block_instance
  G->>+UI: udf_block_instance.process()
  UI->>+P1: process()
  Note over P1: execute process()
  P1->>P2: Request
  Note over P2: execute user defined function
  P2-->>P1: params or series
  P1-->>-UI: BlockGlue(params, series)
  UI-->>-G: block_glue_instance
```


Up to this point, the use of the `@block` decorator with classes such as UdfClass has described, but using the Block class on its own is not intended. Please read the following explanation of the `Flow` class for more details.

## About `Flow`-class

> Blocks are meant to be combined.

Processes always consist of combinations of multiple simple operations. And the only tedious part is aligning their inputs and outputs.

Therefore, in `Flow`-class, it automatically resolves the sequence of those processes for users, as long as you provide the initial values.

## usage

```python
import kabutobashi as kb

# n日前までの営業日の日付リストを取得する関数
target_date = "2020-01-01"
date_list = kb.get_past_n_days(target_date, n=40)
```

## initialize Database

```python
import kabutobashi as kb
kb.KabutobashiDatabase().initialize()

# add data
kb.crawl_info_multiple(code="1375", page="1", database_dir="...")
kb.crawl_info_multiple(code="1375", page="2", database_dir="...")
kb.crawl_info_multiple(code="1375", page="etc...", database_dir="...")

# add data daily
kb.crawl_info(code="1375", database_dir="...")

# analysis and add data
kb.analysis(code="1375", database_dir="...")
```
