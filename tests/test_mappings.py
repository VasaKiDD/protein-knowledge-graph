import pytest

from pybiographs import Mappings


@pytest.fixture()
def mappings():
    return Mappings()


class TestMappings:
    def test_names(self, mappings):
        for name in mappings.names:
            assert getattr(mappings, "_%s" % name) is None
            val = getattr(mappings, name)
            isinstance(val, dict)
