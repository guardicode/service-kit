from collections.abc import Sequence
from typing import Final, TypeAlias

import pytest
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from service_kit.configuration import ListConfigurationType, ServiceConfiguration
from service_kit.logging import LogLevel


@pytest.mark.parametrize("generic_type, expected", ((int, (1, 2, 3)), (str, ("1", "2", "3"))))
def test_list_configuration_type__generic(generic_type: TypeAlias, expected: Sequence):
    class _TestIntListConfigurationType(BaseSettings):
        f1: ListConfigurationType[generic_type]

    config = _TestIntListConfigurationType(f1="1,2,3")

    assert config.f1 == expected


class _TestStrListConfigurationType(BaseSettings):
    model_config = SettingsConfigDict(env_parse_none_str="None", env_prefix="TEST_", extra="ignore")
    f1: ListConfigurationType[str]


F1_ENV_VAR: Final[str] = "TEST_F1"


@pytest.mark.parametrize(
    "unparsed, parsed",
    [
        ['["single_column"]', ("single_column",)],
        ["single_column", ("single_column",)],
        ['["a","b", "c"]', ("a", "b", "c")],
        ["a,b,c", ("a", "b", "c")],
        ["a , b,c", ("a", "b", "c")],
        ["c , z, b, a", ("c", "z", "b", "a")],
        ["a,b,3", ("a", "b", "3")],
        ["", tuple()],
        [",", tuple()],
        ["[]", tuple()],
    ],
)
def test_string_list_variable(
    monkeypatch: pytest.MonkeyPatch, unparsed: str, parsed: Sequence[str]
):
    monkeypatch.setenv(F1_ENV_VAR, unparsed)

    config = _TestStrListConfigurationType()

    assert config.f1 == parsed


def test_unset_list_variable(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(F1_ENV_VAR, raising=False)

    with pytest.raises(ValueError) as err:
        _TestStrListConfigurationType()

    assert "f1" in str(err.value)
    assert "missing" in str(err.value)


class _TestDebugOverrides(ServiceConfiguration):
    model_config = SettingsConfigDict(env_parse_none_str="None", env_prefix="TEST_", extra="ignore")


def test_debug_true_overrides_log_level():
    config = _TestDebugOverrides(
        debug=True,
        log_directory=None,
        log_level=LogLevel.CRITICAL,
        pretty_print_logs=False,
    )

    assert config.debug
    assert config.log_level == LogLevel.TRACE


def test_debug_false_does_not_override_log_level():
    config = _TestDebugOverrides(
        debug=False,
        log_directory=None,
        log_level=LogLevel.CRITICAL,
        pretty_print_logs=False,
    )

    assert not config.debug
    assert config.log_level == LogLevel.CRITICAL


def test_config_remains_frozen():
    config = _TestDebugOverrides(
        debug=True,
        log_directory=None,
        log_level=LogLevel.CRITICAL,
        pretty_print_logs=False,
    )

    with pytest.raises(ValidationError) as err:
        config.debug = False

    assert "frozen" in str(err.value)
