from typing import Any, Final

import pytest

from service_kit import StructuredError

MESSAGE: Final[str] = "test error"
PARAM1: Final[str] = "p1"
PARAM2: Final[str] = "p2"
STRUCTURED_ERROR: Final[StructuredError] = StructuredError(MESSAGE, param1=PARAM1, param2=PARAM2)

EXPECTED_STRUCTURED_ERROR: dict[str, Any] = {"message": MESSAGE, "param1": PARAM1, "param2": PARAM2}


def test_strucured_error():
    assert STRUCTURED_ERROR.structured_error == EXPECTED_STRUCTURED_ERROR


def test_attributes():
    assert STRUCTURED_ERROR.message == MESSAGE
    assert STRUCTURED_ERROR.param1 == PARAM1
    assert STRUCTURED_ERROR.param2 == PARAM2


def test_unknown_attribute():
    with pytest.raises(AttributeError):
        STRUCTURED_ERROR.unknown


def test_str():
    assert str(STRUCTURED_ERROR) == MESSAGE
