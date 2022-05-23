import os

from kabutobashi.domain.values import StockRecordset
from kabutobashi.infrastructure.repository import StockRecordsetStorageBasicRepository

PARENT_PATH = os.path.abspath(os.path.dirname(__file__))
SOURCE_PATH = os.path.abspath(os.path.dirname(PARENT_PATH))
DATA_PATH = f"{SOURCE_PATH}/data"


def example() -> StockRecordset:
    """

    Examples:
        >>> import kabutobashi as kb
        >>> records = kb.example()
        >>> agg = kb.StockCodeSingleAggregate.of(entity=records, code="1375")
        >>> processed = agg.with_processed(kb.methods)
    """
    file_name = "example.csv.gz"
    return StockRecordsetStorageBasicRepository(f"{DATA_PATH}/{file_name}").read()
