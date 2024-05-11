import pytest

from kabutobashi import block
from kabutobashi.domain.errors import KabutobashiBlockDecoratorNameError


def test_udf_block_decorator_basics():

    @block()
    class UdfBlock:

        def _process(self):
            pass

    udf_block = UdfBlock()
    assert "series" in udf_block.__dict__
    assert "params" in udf_block.__dict__
    assert udf_block.block_name == "udf_block"


def test_udf_block_decorator_name_error():
    # class must end with `Block`

    with pytest.raises(KabutobashiBlockDecoratorNameError):

        @block()
        class UdfBlock2:

            def _process(self):
                pass

    with pytest.raises(KabutobashiBlockDecoratorNameError):

        @block()
        class Udfblock:

            def _process(self):
                pass
