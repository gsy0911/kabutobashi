.. kabutobashi documentation master file, created by
   sphinx-quickstart on Sat Jun 20 09:41:12 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

kabutobashi
===========

code status

.. image:: https://github.com/gsy0911/kabutobashi/workflows/pytest/badge.svg
    :target: https://github.com/gsy0911/kabutobashi/actions?query=workflow%3Apytest

.. image:: https://codecov.io/gh/gsy0911/kabutobashi/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/gsy0911/kabutobashi

.. image:: https://readthedocs.org/projects/kabutobashi/badge/?version=latest
    :target: https://kabutobashi.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

package status

.. image:: https://img.shields.io/badge/python-3.7|3.8|3.9-blue.svg
   :target: https://www.python.org/downloads/release/python-377/

.. image:: https://img.shields.io/pypi/v/kabutobashi.svg
    :target: https://pypi.org/project/kabutobashi/

.. image:: https://pepy.tech/badge/kabutobashi
   :target: https://pepy.tech/project/kabutobashi


**kabutobashi** is to provide convenient Python functions for analyze stocks.

``kabutobashi`` can

* crawl Japanese stock data
* analyze stock based on charts

Installation
============

**kabutobashi** can be installed from pip.

.. code-block:: shell

   pip install kabutobashi


Usage
=====


Analysis
--------

.. code-block:: python
    
    import kabutobashi as kb

    # サンプルデータの取得
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



Crawling
--------

Get Japanese-Stock-Market info.

.. code-block:: python

    import kabutobashi as kb
    

Visualize
---------


Not Yet.


Utilities
---------

.. code-block:: python

    import kabutobashi as kb

    # n日前までの営業日の日付リストを取得する関数
    target_date = "2020-01-01"
    date_list = kb.get_past_n_days(target_date, n=40)
    

For Users
=========

.. toctree::
   :maxdepth: 2

   sources/api
