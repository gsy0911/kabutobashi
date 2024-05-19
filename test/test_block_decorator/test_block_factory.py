from kabutobashi import block
from kabutobashi.domain.entity.blocks import BlockGlue


@block(block_name="udf")
class UdfBlock:
    term: int = 10

    def _process(self):
        pass


def test_udf_block_decorator_factory():
    udf_block = UdfBlock.factory(BlockGlue(params={"udf": {"term": 1000}}))
    assert udf_block.term == 1000
    assert udf_block._glue is not None
    assert udf_block._glue.params["udf"]["term"] == 1000
    assert udf_block.params["term"] == 1000
