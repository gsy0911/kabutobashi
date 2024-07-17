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


.. mermaid::

   sequenceDiagram
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



Utilities
---------

.. code-block:: python

    import kabutobashi as kb

    target_date = "2020-01-01"
    date_list = kb.get_past_n_days(target_date, n=40)


Other
=====

.. toctree::
   :maxdepth: 2

   sources/release
