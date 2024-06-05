import pandas as pd

from kabutobashi.domain.entity.blocks import BlockGlue, BlockOutput


def test_block_glue():
    # check1
    df1 = pd.DataFrame.from_dict({"col1": [1, 2], "col2": [3, 4]})
    df2 = pd.DataFrame.from_dict({"col1": [5, 6], "col3": [3, 4]})
    output1 = BlockOutput(series=df1, params=None, block_name="output1", execution_order=1)
    output2 = BlockOutput(series=df2, params=None, block_name="output2", execution_order=2)
    block_glue = BlockGlue(
        series=None, params=None, block_outputs={"output1": output1, "output2": output2}, execution_order=1
    )

    # assert df
    fixed_df = block_glue.get_series_from_required_columns(required_columns=["col1", "col2", "col3"])
    assert1_df = pd.DataFrame.from_dict({"col1": [5, 6], "col2": [3, 4], "col3": [3, 4]})
    assert fixed_df.equals(assert1_df)
    fixed_df = block_glue.get_series_from_required_columns(required_columns=["col2", "col3"])
    assert2_df = pd.DataFrame.from_dict({"col2": [3, 4], "col3": [3, 4]})
    assert fixed_df.equals(assert2_df)

    # check2
    df3 = pd.DataFrame.from_dict({"col1": [7, 8], "col4": ["a", "b"]})
    output3 = BlockOutput(series=df3, params=None, block_name="output3", execution_order=3)
    block_glue = BlockGlue(
        series=None,
        params=None,
        block_outputs={"output1": output1, "output2": output2, "output3": output3},
        execution_order=1,
    )

    fixed_df = block_glue.get_series_from_required_columns(required_columns=["col1", "col2", "col3", "col4"])
    assert3_df = pd.DataFrame.from_dict({"col1": [7, 8], "col2": [3, 4], "col3": [3, 4], "col4": ["a", "b"]})
    assert fixed_df.equals(assert3_df)
