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

.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/
    :alt: Imports: isort

.. image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :target: http://mypy-lang.org/
    :alt: Checked with mypy


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
* analyze, visualize and parameterize stock based on charts

Installation
============

**kabutobashi** can be installed from pip.

.. code-block:: shell

   pip install kabutobashi


Concept
=======

- ``E``: Entity
- ``VO``: ValueObject
- ``S``: Service
- ``A``: Aggregate

.. mermaid::

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


Usage
=====

Crawling
--------

Get Japanese-Stock-Market info.

.. code-block:: python

    import kabutobashi as kb
    stock_info = kb.crawl_info(code="1234")
    ipo_info = kb.crawl_ipo(year="2022")


Analysis
--------

.. code-block:: python

    import kabutobashi as kb

    df = kb.example()
    StockCodeSingleAggregate.of(entity=df, code=1375).to_processed(kb.methods)
    print(processed.get_impact())



Visualize
---------


You can use, but Not Completed Yet.

.. code-block:: python

    import kabutobashi as kb
    df = kb.example()
    sdp = StockCodeSingleAggregate.of(entity=df, code=1375).to_processed([kb.sma, kb.macd])
    sdp.visualize()



Utilities
---------

.. code-block:: python

    import kabutobashi as kb

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
