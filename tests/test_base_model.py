import pytest
from pydantic import ValidationError

from service_kit.base_model import MutableServiceKitBaseModel, ServiceKitBaseModel

SENSITIVE_INPUT = "super-secret-value"


class ChildModel(ServiceKitBaseModel):
    number: int


class MutableChildModel(MutableServiceKitBaseModel):
    number: int


@pytest.mark.parametrize("model_class", [ChildModel, MutableChildModel])
def test_input_hidden_in_validation_errors(model_class):
    with pytest.raises(ValidationError) as exc_info:
        model_class(number=SENSITIVE_INPUT)

    assert SENSITIVE_INPUT not in str(exc_info.value)
