from kabutobashi import block
from kabutobashi.domain.entity.blocks import BlockGlue


@block(block_name="udf")
class UdfBlock:
    term: int = 10

    def _process(self) -> dict:
        return {"udf_term": 1000}


@block(block_name="post_udf", pre_condition_block_name="udf")
class PostUdfBlock:
    post_term: int = 10

    def _process(self) -> dict:
        return {"post_udf_term": 1000}


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
