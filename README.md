# kabutobashi

[![pytest](https://github.com/gsy0911/kabutobashi/workflows/pytest/badge.svg)](https://github.com/gsy0911/kabutobashi/actions?query=workflow%3Apytest)
[![codecov](https://codecov.io/gh/gsy0911/kabutobashi/branch/main/graph/badge.svg)](https://codecov.io/gh/gsy0911/kabutobashi)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

[![PythonVersion](https://img.shields.io/pypi/pyversions/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![PiPY](https://img.shields.io/pypi/v/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![Documentation Status](https://readthedocs.org/projects/kabutobashi/badge/?version=latest)](https://kabutobashi.readthedocs.io/en/latest/?badge=latest)

## concept

class-relationship.

- `E`: Entity
- `VO`: ValueObject
- `S`: Service
- `A`: Aggregate

```mermaid
graph TD;
  
  subgraph Stock
    stock[Stock:E]
    brand[StockBrand:E]
    record[StockRecord:E]
    indicator[StockIndicator:E]
    
    stock --> brand
    stock --> record
    stock --> indicator
  end

  subgraph Stock-to-Analysis
    aggregate[StockCodeSingleAggregate:A]
    processed[StockDataProcessed:VO]
    estimated[StockDataEstimated:VO]
    
    aggregate --- |Info| stock
    aggregate --- |Method| processed
    aggregate --- |Analysis| estimated
  end

  subgraph Repositories/Storage
    repositories[(Storage/Database)] --- | read/write | stock
  end

  subgraph Pages
    raw_html[RawHtml:VO]
    decoder[Decoder:S]
    decoded_html[DecodedHtml:VO]

    raw_html --> decoder
    decoder --> decoded_html
    decoded_html --> repositories
    decoded_html --> stock
  end

  subgraph Repositories/Web
    web[[Web]] --> | crawl | raw_html
  end
```


## usage

```python
import kabutobashi as kb

df = kb.example()
methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
analysis = kb.stock_analysis
agg = kb.StockCodeSingleAggregate.of(entity=df, code="1234").with_processed(methods).with_estimated(stock_analysis=analysis)
print(agg)

# n日前までの営業日の日付リストを取得する関数
target_date = "2020-01-01"
date_list = kb.get_past_n_days(target_date, n=40)

```


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

    def _process(self):
        return {"doubled_term": self.term * 2}
    
    def process(self):
        return self._process()

    def factory(self, glue: BlockGlue) -> "UdfBlock":
        # Omitted. In reality, processes are described.
        ...

    def _factory(self, glue: BlockGlue) -> "UdfBlock":
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


Up to this point, the use of the `@block` decorator with classes such as UdfClass has described, but using the Block class on its own is not intended. Please read the following explanation of the `Flow` class for more details.

### Read-Block

- input
  - params
- output
  - series

### Crawl-Block

- input
  - params
- output
  - output.params

### Extract-Block

- input
  - params
- output
  - output.params

### PreProcess-Block

- input
  - series
  - params
- output
  - series

### Process-Block

- input
  - series
  - params
- output
  - output.series

### Parameterize-Block

- input
  - series
  - params
- output
  - output.params

### Reduce-Block

- input
  - series
  - params
- output
  - params

## About `Flow`-class

> Blocks are meant to be combined.

Processes always consist of combinations of multiple simple operations. And the only tedious part is aligning their inputs and outputs.

Therefore, in `Flow`-class, it automatically resolves the sequence of those processes for users, as long as you provide the initial values.

