from kabutobashi.domain.entity import StockDataRepository, StockDataMultipleCode
import os

# pytestの設定
PARENT_PATH = os.path.abspath(os.path.dirname(__file__))
SOURCE_PATH = os.path.abspath(os.path.dirname(PARENT_PATH))
DATA_PATH = f"{SOURCE_PATH}/data"


def example() -> StockDataMultipleCode:
    """

    Examples:
        >>> import kabutobashi as kb
        >>> sdmc = kb.example()
        >>> sdmc.to_single_code(1375).to_processed([kb.sma, kb.macd])
    """
    file_name = "example.csv.gz"
    print(SOURCE_PATH)
    return StockDataRepository().read(f"{DATA_PATH}/{file_name}")
