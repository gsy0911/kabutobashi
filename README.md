# kabutobashi

[![pytest](https://github.com/gsy0911/kabutobashi/workflows/pytest/badge.svg)](https://github.com/gsy0911/kabutobashi/actions?query=workflow%3Apytest)
[![codecov](https://codecov.io/gh/gsy0911/kabutobashi/branch/master/graph/badge.svg)](https://codecov.io/gh/gsy0911/kabutobashi)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

[![PythonVersion](https://img.shields.io/pypi/pyversions/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![PiPY](https://img.shields.io/pypi/v/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![Documentation Status](https://readthedocs.org/projects/kabutobashi/badge/?version=latest)](https://kabutobashi.readthedocs.io/en/latest/?badge=latest)

## concept

class-relationship.

```mermaid
graph TD;
  web[[Web]] --> | crawl | sdmc
  repo[(Storage)] --- | read/write | sdmc
  sdmc[StockDataMultipleCode] --> | code | sdsc
  sdsc[StockDataSingleCode] -.-> | Method | ps
  ps[Processed-Single] -.- | multiple | pm
  sdsc --> | Methods | pm
  pm[Processed-Multiple] -.-> | Filters | es
  es[Estimated-Single] -.- | multiple | em[Estimated-Multiple]
  pm --> | Filters | em
  sdmc ==> | Methods | pm
  sdmc ==> | Methods,Filters | em
```

- StockDataMultipleCode 
  - contains multiple code & multiple date
- StockDataSingleCode
  - contains single code & multiple date
- Processed (Single)
  - is from `StockDataSingleCode` using single `Method`
- Processed (Multiple)
  - is from `StockDataSingleCode` using multiple `Method`
- Estimated (Single)
  - is from `Processed (Multiple)` using single `EstimateFilter`
- Estimated (Multiple)
  - is from `Processed (Multiple)` using multiple `EstimateFilter`

## usage

```python
import kabutobashi as kb

file_path_list = [...]
sdmc = kb.reader.csv(file_path_list)
for sdsc in sdmc.to_code_iterable():
    processed = sdsc.to_processed(methods=kb.methods)
    print(processed.get_impact())


# n日前までの営業日の日付リストを取得する関数
target_date = "2020-01-01"
date_list = kb.get_past_n_days(target_date, n=40)

```
