import pandas as pd

from kabutobashi import Flow, block
from kabutobashi.domain.entity.blocks import BlockGlue


@block(block_name="udf")
class UdfBlock:
    term: int = 10

    def _process(self) -> dict:
        return {"udf_term": 1000}


@block(block_name="post_1_udf", pre_condition_block_name="udf")
class Post1UdfBlock:
    post_term: int = 10

    def _process(self) -> pd.DataFrame:
        return pd.DataFrame([{"post_1_udf_term": 100}])


@block(block_name="post_2_udf", pre_condition_block_name="post_1_udf")
class Post2UdfBlock:
    post_term: int = 10
    series: pd.DataFrame

    def _process(self) -> pd.DataFrame:
        return pd.DataFrame([{"post_2_udf_term": 1000}])


def test_udf_block_decorator_factory_and_glue():
    # check factory
    udf_block = UdfBlock.factory(BlockGlue(params={"udf": {"term": 1000}}))
    assert udf_block.term == 1000
    assert udf_block._glue is not None
    assert udf_block._glue.params["udf"]["term"] == 1000
    assert udf_block.params["term"] == 1000

    result = udf_block._process()
    assert type(result) == dict
    assert result["udf_term"] == 1000

    # check glue-response
    udf_glue = UdfBlock.glue(BlockGlue(params={"udf": {"term": 1000}}))
    assert udf_glue.block_outputs is not None
    assert udf_glue.block_outputs["udf"] is not None
    assert udf_glue.block_outputs["udf"].params["udf_term"] == 1000


def test_udf_block_with_flow():
    blocks = [
        UdfBlock,
        Post1UdfBlock,
        Post2UdfBlock,
    ]

    res = Flow.initialize(params={"udf": {"term": 1000}}).then(blocks)
    res_1_series = res.block_glue.block_outputs["post_1_udf"].series
    assert res_1_series is not None
    assert "post_1_udf_term" in res_1_series.columns
    res_2_series = res.block_glue.block_outputs["post_2_udf"].series
    assert res_2_series is not None
    assert "post_2_udf_term" in res_2_series.columns
    # check BlockGlue
    assert "post_1_udf" in res.block_glue
    res_1_series = res.block_glue["post_1_udf"].series
    assert "post_1_udf_term" in res_1_series.columns
    assert "post_2_udf" in res.block_glue
    res_2_series = res.block_glue["post_2_udf"].series
    assert "post_2_udf_term" in res_2_series.columns
    # check __len__
    assert len(res.block_glue) == 4
