import pytest

from service_kit import ServiceKitBaseModel
from service_kit.configuration import FeatureFlag


class FeatureFlags(ServiceKitBaseModel):
    flag_name: FeatureFlag = FeatureFlag(enabled=True)


FEATURE_FLAG_OBJECT = FeatureFlags(flag_name=True)
FEATURE_FLAG_DICT_OUT = {"flag_name": True}


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ("true", "1"):
            return True
        elif value_lower in ("false", "0"):
            return False
    if isinstance(value, int):
        return bool(value)
    raise ValueError(f"Cannot convert {value} to boolean.")


@pytest.mark.parametrize("bool_value", [True, False, 1, 0, "false", "true", "True", "False"])
def test_feature_flag(bool_value):
    flags = FeatureFlags(flag_name=bool_value)

    assert isinstance(flags.flag_name, FeatureFlag)
    assert flags.flag_name.enabled is str_to_bool(bool_value)


def test_feature_flag__serialization():
    assert FEATURE_FLAG_OBJECT.to_json_dict() == FEATURE_FLAG_DICT_OUT


def test_feature_flag__deserialization():
    assert FeatureFlags(**FEATURE_FLAG_DICT_OUT) == FEATURE_FLAG_OBJECT


@pytest.mark.parametrize("bool_value", [True, False])
def test_feature_flag__with_feature_flag(bool_value):
    flasgs = FeatureFlags(flag_name=FeatureFlag(enabled=bool_value))

    assert isinstance(flasgs.flag_name, FeatureFlag)
    assert flasgs.flag_name.enabled is bool_value
