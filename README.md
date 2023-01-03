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
