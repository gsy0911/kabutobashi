# pystock

[![CircleCI](https://circleci.com/gh/gsy0911/pystock.svg?style=svg&circle-token=76679803b77f4fc6e722c952a20da7fc5f0294c7)](https://circleci.com/gh/gsy0911/pystock)
[![codecov](https://codecov.io/gh/gsy0911/pystock/branch/master/graph/badge.svg)](https://codecov.io/gh/gsy0911/pystock)

## Development Environment
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#github.com/gsy0911/pystock)

## usage

```python
import pystock as ps

# 例データの取得
df_stock = ps.example_data()
# 分析手法
analysis_methods = [
    ps.macd, 
    ps.sma, 
    ps.stochastics, 
    ps.adx, 
    ps.bollinger_bands, 
    ps.momentum, 
    ps.psycho_logical
]
ps.get_impact_with(df_stock, analysis_methods)

# n日前までの営業日の日付リストを取得する関数
target_date = "2020-01-01"
date_list = ps.get_past_n_days(target_date, n=40)
```
