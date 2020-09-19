# kabutobashi

[![pytest](https://github.com/gsy0911/kabutobashi/workflows/pytest/badge.svg)](https://github.com/gsy0911/kabutobashi/actions?query=workflow%3Apytest)
[![codecov](https://codecov.io/gh/gsy0911/kabutobashi/branch/master/graph/badge.svg)](https://codecov.io/gh/gsy0911/kabutobashi)

[![PythonVersion](https://img.shields.io/badge/python-3.7|3.8-blue.svg)](https://www.python.org/downloads/release/python-377/)
[![PiPY](https://img.shields.io/pypi/v/kabutobashi.svg)](https://pypi.org/project/kabutobashi/)
[![Documentation Status](https://readthedocs.org/projects/kabutobashi/badge/?version=latest)](https://kabutobashi.readthedocs.io/en/latest/?badge=latest)


## Development Environment
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#github.com/gsy0911/kabutobashi)

## usage

```python
import kabutobashi as kb

# 例データの取得
df_stock = kb.example_data()
# 分析手法
analysis_methods = [
    kb.macd, 
    kb.sma, 
    kb.stochastics, 
    kb.adx, 
    kb.bollinger_bands, 
    kb.momentum, 
    kb.psycho_logical
]
kb.get_impact_with(df_stock, analysis_methods)

# n日前までの営業日の日付リストを取得する関数
target_date = "2020-01-01"
date_list = kb.get_past_n_days(target_date, n=40)
```
