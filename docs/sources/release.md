# Release Note

## 0.7.2

- FIX: sort values by `dt` ([#168](https://github.com/gsy0911/kabutobashi/issues/168))

## 0.7.1

- FIX: catch additional error ([#167](https://github.com/gsy0911/kabutobashi/issues/167))

## 0.7.0

- ENHANCEMENT: use Pydantic v2 ([#166](https://github.com/gsy0911/kabutobashi/issues/166))

## 0.6.5

- ENHANCEMENT: add stock-market-enum ([#159](https://github.com/gsy0911/kabutobashi/issues/159))
- FIX: document works

## 0.6.4

- ENHANCEMENT: add `to_dict()` to `StockAgg` ([#153](https://github.com/gsy0911/kabutobashi/issues/153))
- ENHANCEMENT: remove unused `serialize-method` ([#154](https://github.com/gsy0911/kabutobashi/issues/154))
- ENHANCEMENT: rename `DecodeHtmlPage` and `RawHtmlPage` ([#155](https://github.com/gsy0911/kabutobashi/issues/155))
- ENHANCEMENT: add DecodedHtmlPageStockInfoMultipleDays ([#156](https://github.com/gsy0911/kabutobashi/issues/156))
- ENHANCEMENT: add `repository` to crawl multiple pages ([#157](https://github.com/gsy0911/kabutobashi/issues/157))

## 0.6.3

- BUG FIX: `_get_impact` function
- BUG FIX: remove unused `index` column ([#151](https://github.com/gsy0911/kabutobashi/issues/151))
- BUG FIX: add missing columns ([#152](https://github.com/gsy0911/kabutobashi/issues/152))


## 0.6.2

- BUG FIX: pattern match result check

## 0.6.1

- ENHANCEMENT: add Service to convert ValueObject to Entity ([#149](https://github.com/gsy0911/kabutobashi/issues/149))
- ENHANCEMENT: add application to get code-list ([#150](https://github.com/gsy0911/kabutobashi/issues/150))

## 0.6.0

- ENHANCEMENT: modify codecov ([#135](https://github.com/gsy0911/kabutobashi/issues/135))
- ENHANCEMENT: add Serialize-method ([#136](https://github.com/gsy0911/kabutobashi/issues/136))
- ENHANCEMENT: add `Html`-decoded-ValueObject ([#138](https://github.com/gsy0911/kabutobashi/issues/138))
- ENHANCEMENT: remove `52WeeksHighLow` related ([#143](https://github.com/gsy0911/kabutobashi/issues/143))
- ENHANCEMENT: add `Stock`-Entity ([#144](https://github.com/gsy0911/kabutobashi/issues/144))
- ENHANCEMENT: add `IpoPage`-ValueObject ([#145](https://github.com/gsy0911/kabutobashi/issues/145))
- ENHANCEMENT: replace directory,files and docs ([#146](https://github.com/gsy0911/kabutobashi/issues/146))
- ENHANCEMENT: add pplication using ``injection`` ([#147](https://github.com/gsy0911/kabutobashi/issues/147))
- ENHANCEMENT: public utilities function ([#148](https://github.com/gsy0911/kabutobashi/issues/148))


## 0.5.2

- ENHANCEMENT: modify `get_impact()` ([#133](https://github.com/gsy0911/kabutobashi/issues/133))
- ENHANCEMENT: update attribute `delisting` ([#132](https://github.com/gsy0911/kabutobashi/issues/132))
- ENHANCEMENT: add test on Python 3.10 ([#131](https://github.com/gsy0911/kabutobashi/issues/131))
- ENHANCEMENT: add IDictSerialize ([#130](https://github.com/gsy0911/kabutobashi/issues/130))
- ENHANCEMENT: add infrastructure on HtmlPages ([#119](https://github.com/gsy0911/kabutobashi/issues/119))

## 0.5.1

- ENHANCEMENT: add lint and update packages ([#126](https://github.com/gsy0911/kabutobashi/issues/126))
- BUG FIX: crawl `market` ([#125](https://github.com/gsy0911/kabutobashi/issues/125))
- ENHANCEMENT: update stock-recordset requirement ([#124](https://github.com/gsy0911/kabutobashi/issues/124))

## 0.5.0

- rename classes ([#121](https://github.com/gsy0911/kabutobashi/issues/121))
- update document ([#120](https://github.com/gsy0911/kabutobashi/issues/120))
- modify recordset repository ([#118](https://github.com/gsy0911/kabutobashi/issues/118))
- fix error ([#117](https://github.com/gsy0911/kabutobashi/issues/117))
- Method contains MethodProcess and MethodVisualize ([#116](https://github.com/gsy0911/kabutobashi/issues/116))
- remove `StockDataSingleCode` ([#115](https://github.com/gsy0911/kabutobashi/issues/115))

## 0.4.5

- modify method name ([#114](https://github.com/gsy0911/kabutobashi/issues/114))
- add is_delisting ([#113](https://github.com/gsy0911/kabutobashi/issues/113))

## 0.4.4

- error: code is float-string, like "1000.0" ([#112](https://github.com/gsy0911/kabutobashi/issues/112))
- crawl previous stock info ([#104](https://github.com/gsy0911/kabutobashi/issues/104))

## 0.4.3

- modify errors and partially DDD ([#111](https://github.com/gsy0911/kabutobashi/issues/111))

## 0.4.2

- modify errors and partially DDD ([#106](https://github.com/gsy0911/kabutobashi/issues/106))

## 0.4.1

- modify errors ([#105](https://github.com/gsy0911/kabutobashi/issues/105))

## 0.4.0

- add DDD and CleanArchitecture ([#103](https://github.com/gsy0911/kabutobashi/issues/103))

## 0.3.4

- modify Error ([#98](https://github.com/gsy0911/kabutobashi/issues/98))

## 0.3.3

- modify Error ([#98](https://github.com/gsy0911/kabutobashi/issues/98))

## 0.3.2

- modify KeyError ([#98](https://github.com/gsy0911/kabutobashi/issues/98))
- refactor: `code` name ([#96](https://github.com/gsy0911/kabutobashi/issues/96))
- update document ([#95](https://github.com/gsy0911/kabutobashi/issues/95))
- parallel estimated ([#93](https://github.com/gsy0911/kabutobashi/issues/93))

## 0.3.1

- add `crawl()` in `StockDataMultipleCode` ([#89](https://github.com/gsy0911/kabutobashi/issues/89))
- modify `Basic` methods, `volume` type ([#92](https://github.com/gsy0911/kabutobashi/issues/92))
- add function to concat `filter_name` ([#88](https://github.com/gsy0911/kabutobashi/issues/88))
- modify `to_code_iterable` ([#90](https://github.com/gsy0911/kabutobashi/issues/90))
- update README ([#87](https://github.com/gsy0911/kabutobashi/issues/87))

## 0.3.0

- multiprocessing `IStockDataMultipleCodeReader` ([#86](https://github.com/gsy0911/kabutobashi/issues/86))
- multiprocessing `StockInfoPage` ([#85](https://github.com/gsy0911/kabutobashi/issues/85))
- add `Estimated` and `EstimateFilter` ([#84](https://github.com/gsy0911/kabutobashi/issues/84))
- merge `Parameterized` and `Processed` ([#83](https://github.com/gsy0911/kabutobashi/issues/83))


## 0.2.6

- re-implement `Fitting(Method)` ([#44](https://github.com/gsy0911/kabutobashi/issues/44))
- add `to_parameterize` ([#81](https://github.com/gsy0911/kabutobashi/issues/81))
- add `read()` and `write()` in `StockDataMultipleCode` ([#82](https://github.com/gsy0911/kabutobashi/issues/82))

## 0.2.5

- add `contains_outlier-flag` ([#80](https://github.com/gsy0911/kabutobashi/issues/80))
- add `get_df()` in `StockDataMultipleCode` ([#80](https://github.com/gsy0911/kabutobashi/issues/80))

## 0.2.4


- add `stop-updating-flag` ([#76](https://github.com/gsy0911/kabutobashi/issues/76))
- implements `save()` function ([#74](https://github.com/gsy0911/kabutobashi/issues/74))
- add `mypy` ([#75](https://github.com/gsy0911/kabutobashi/issues/75))
- fix `visualize()` function ([#68](https://github.com/gsy0911/kabutobashi/issues/68))
- add new `index` value ([#70](https://github.com/gsy0911/kabutobashi/issues/70))


## 0.2.3

- re-build entities ([#65](https://github.com/gsy0911/kabutobashi/issues/65))
- add `visualize()` function ([#49](https://github.com/gsy0911/kabutobashi/issues/49))
- compatibility to M1 mac ([#67](https://github.com/gsy0911/kabutobashi/issues/67))
- drop Python 3.7 ([#55](https://github.com/gsy0911/kabutobashi/issues/55))

## 0.2.2

- BUG FIX: Week52HighLow validator ([#62](https://github.com/gsy0911/kabutobashi/issues/62))

## 0.2.1

- add release note ([#56](https://github.com/gsy0911/kabutobashi/issues/56))
- beautifulsoup argument ([#57](https://github.com/gsy0911/kabutobashi/issues/57))
- add `isort` ([#59](https://github.com/gsy0911/kabutobashi/issues/59))
- add `name` to StockInfo ([#61](https://github.com/gsy0911/kabutobashi/issues/61))
- modify read_function `_decode_stock_data` ([#58](https://github.com/gsy0911/kabutobashi/issues/58))

## 0.2.0

- Replace metaclass by dataclasses ([#27](https://github.com/gsy0911/kabutobashi/issues/27))
