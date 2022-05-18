# kabutobashi

[![pytest](https://github.com/gsy0911/kabutobashi/workflows/pytest/badge.svg)](https://github.com/gsy0911/kabutobashi/actions?query=workflow%3Apytest)
[![codecov](https://codecov.io/gh/gsy0911/kabutobashi/branch/master/graph/badge.svg)](https://codecov.io/gh/gsy0911/kabutobashi)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

[![PythonVersion](https://img.shields.io/pypi/pyversions/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![PiPY](https://img.shields.io/pypi/v/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![Documentation Status](https://readthedocs.org/projects/kabutobashi/badge/?version=latest)](https://kabutobashi.readthedocs.io/en/latest/?badge=latest)

## concept

class-relationship.

```mermaid
graph TD;
  subgraph Aggregates
    aggregate[StockCodeSingleAggregate]
    aggregate --- single
    aggregate --- |Method| processed
    aggregate --- |Filter| filtered
     
    subgraph ValueObject
      single[StockDataSingleCode]
      processed[StockDataProcessed]
      filtered[StockDataFiltered]
    end
  end
  
  subgraph Entities
    recordset[StockRecordset]
    brand[StockBrand]
    record[StockRecord]
    
    recordset --> brand
    recordset --> record
    recordset ---> aggregate
  end

  subgraph Repositories
    web[[Web]] --- | crawl | recordset
    repositories[(Storage/Database)] --- | read/write | recordset
    
    repositories --- | read/write | aggregate
  end
```


## usage

```python
import kabutobashi as kb

records = kb.example()
methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
filters = kb.estimate_filters
for df in records.to_code_iterable():
    agg = kb.StockCodeSingleAggregate.of(entity=df).with_processed(methods).with_estimated(filters)
    print(agg)

# n日前までの営業日の日付リストを取得する関数
target_date = "2020-01-01"
date_list = kb.get_past_n_days(target_date, n=40)

```
