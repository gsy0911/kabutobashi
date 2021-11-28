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

.. image:: https://img.shields.io/pypi/pyversions/kabutobashi.svg
   :target: https://pypi.org/project/kabutobashi/

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

   file_path_list = [...]
   sdmc = kb.StockDataRepository().read(file_path_list)
   for sdsc in sdmc.to_code_iterable():
      processed = sdsc.to_processed(methods=kb.methods)
      print(processed.get_impact())



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


Other
=====

.. toctree::
   :maxdepth: 2

   sources/release
