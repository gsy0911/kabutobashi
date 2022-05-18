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


Usage
=====


Analysis
--------

.. code-block:: python

    import kabutobashi as kb

    file_path_list = [...]
    sdmc = kb.reader.csv(file_path_list)
    for sdsc in sdmc.to_code_iterable():
        processed = sdsc.to_processed(methods=kb.methods)
        print(processed.get_impact())



Crawling
--------

Get Japanese-Stock-Market info.

.. code-block:: python

    import kabutobashi as kb
    code_list = [...]
    dt = "%Y-%m-%d"
    sdmc = kb.StockDataMultipleData.crawl().get(code_list=code_list, dt=dt)
    

Visualize
---------


You can use, but Not Completed Yet.

.. code-block:: python

    import kabutobashi as kb
    sdmc = kb.example()
    sdp = sdmc.to_single_code(1375).to_processed([kb.sma, kb.macd])
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
