import pytest

from kabutobashi import block
from kabutobashi.domain.errors import KabutobashiBlockDecoratorNameError, KabutobashiBlockDecoratorNotImplementedError


def test_udf_block_decorator_basics():

    @block()
    class UdfBlock:
        term: int = 10

        def _process(self):
            pass

    udf_block = UdfBlock()
    assert "series" in udf_block.__dict__
    assert "params" in udf_block.__dict__
    assert udf_block.block_name == "udf_block"
    assert udf_block.term == 10
    assert udf_block._process is not None
    assert udf_block.process is not None
    assert udf_block._factory is not None
    assert udf_block.factory is not None
    assert udf_block.glue is not None
    assert udf_block.__init__ is not None
    assert udf_block.__repr__ is not None


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


def test_udf_block_decorator_method_not_implemented_error():
    with pytest.raises(KabutobashiBlockDecoratorNotImplementedError) as process_e:

        @block()
        class UdfBlock:
            pass

    assert str(process_e.value) == "_process method is not implemented."

    with pytest.raises(KabutobashiBlockDecoratorNotImplementedError) as factory_e:

        @block(process=False, factory=True)
        class UdfBlock:
            pass

    assert str(factory_e.value) == "_factory method is not implemented."
