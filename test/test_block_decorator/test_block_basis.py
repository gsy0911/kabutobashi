import pandas as pd
import pytest

from kabutobashi.domain.entity.blocks import BlockGlue, BlockOutput
from kabutobashi.domain.errors import KabutobashiBlockGlueError


def test_block_glue():
    block_glue = BlockGlue(series=None, params=None, block_outputs={}, execution_order=1)
    # max_outputs
    assert block_glue.get_max_execution_order() == 0

    # check1
    df1 = pd.DataFrame.from_dict({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame.from_dict({"col1": [5, 6], "col3": [3, 4]})
    output1 = BlockOutput(series=df1, params=None, block_name="output1", execution_order=1)
    output2 = BlockOutput(series=df2, params=None, block_name="output2", execution_order=2)
    block_glue = BlockGlue(
        series=None, params=None, block_outputs={"output1": output1, "output2": output2}, execution_order=1
    )

    # assert df
    fixed_df = block_glue.get_series_from_required_columns(
        required_columns=["col1", "col2", "col3"], series_required_columns_mode="strict"
    )
    assert1_df = pd.DataFrame.from_dict({"col1": [5, 6], "col2": [3, 4], "col3": [3, 4]})
    assert fixed_df.equals(assert1_df)
    fixed_df = block_glue.get_series_from_required_columns(
        required_columns=["col2", "col3"], series_required_columns_mode="strict"
    )
    assert2_df = pd.DataFrame.from_dict({"col2": [3, 4], "col3": [3, 4]})
    assert fixed_df.equals(assert2_df)
    # max_outputs
    assert block_glue.get_max_execution_order() == 2

    # check2
    df3 = pd.DataFrame.from_dict({"col1": [7, 8], "col4": ["a", "b"]})
    output3 = BlockOutput(series=df3, params=None, block_name="output3", execution_order=3)
    block_glue = BlockGlue(
        series=None,
        params=None,
        block_outputs={"output1": output1, "output2": output2, "output3": output3},
        execution_order=1,
    )

    fixed_df = block_glue.get_series_from_required_columns(
        required_columns=["col1", "col2", "col3", "col4"], series_required_columns_mode="strict"
    )
    assert3_df = pd.DataFrame.from_dict({"col1": [7, 8], "col2": [3, 4], "col3": [3, 4], "col4": ["a", "b"]})
    assert fixed_df.equals(assert3_df)
    # max_outputs
    assert block_glue.get_max_execution_order() == 3


def test_block_glue_error():
    # check1
    df1 = pd.DataFrame.from_dict({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame.from_dict({"col1": [5, 6], "col3": [3, 4]})
    output1 = BlockOutput(series=df1, params=None, block_name="output1", execution_order=1)
    output2 = BlockOutput(series=df2, params=None, block_name="output2", execution_order=1)
    block_glue = BlockGlue(
        series=None, params=None, block_outputs={"output1": output1, "output2": output2}, execution_order=1
    )

    # assert df
    with pytest.raises(KabutobashiBlockGlueError) as block_e:
        _ = block_glue.get_series_from_required_columns(
            required_columns=["col1", "col2", "col3"], series_required_columns_mode="strict"
        )
    assert str(block_e.value) == "orders=[1, 1] must be unique."
