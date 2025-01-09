from collections.abc import Sequence
from ipaddress import IPv4Address
from pathlib import Path
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

    config = _TestIntListConfigurationType(f1="1,2,3")  # type: ignore [arg-type]

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

    config = _TestStrListConfigurationType()  # type: ignore[call-arg]

    assert config.f1 == parsed


def test_unset_list_variable(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(F1_ENV_VAR, raising=False)

    with pytest.raises(ValueError) as err:
        _TestStrListConfigurationType()  # type: ignore[call-arg]

    assert "f1" in str(err.value)
    assert "missing" in str(err.value)


class _TestDebugOverrides(ServiceConfiguration):
    model_config = SettingsConfigDict(env_parse_none_str="None", env_prefix="TEST_", extra="ignore")


def test_debug_true_overrides_log_level():
    config = _TestDebugOverrides(
        debug=True,
        log_level=LogLevel.CRITICAL,
    )

    assert config.debug
    assert config.log_level == LogLevel.TRACE


def test_debug_false_does_not_override_log_level():
    config = _TestDebugOverrides(
        debug=False,
        log_level=LogLevel.CRITICAL,
    )

    assert not config.debug
    assert config.log_level == LogLevel.CRITICAL


def test_config_remains_frozen():
    config = _TestDebugOverrides(
        debug=True,
        log_level=LogLevel.CRITICAL,
    )

    with pytest.raises(ValidationError) as err:
        config.debug = False

    assert "frozen" in str(err.value)


def test_config_defaults():
    config = ServiceConfiguration()

    assert config.bind_address == IPv4Address("127.0.0.1")
    assert config.debug is False
    assert config.enable_hot_reload is False
    assert config.log_directory is None
    assert config.log_level == LogLevel.INFO
    assert config.port == 8080
    assert config.pretty_print_logs is True
    assert config.ssl_certfile is None
    assert config.ssl_keyfile is None


def test_custom_values(tmp_path: Path):
    config = ServiceConfiguration(
        bind_address=IPv4Address("192.168.52.52"),
        log_directory=tmp_path / "custom_path",
        log_level="DEBUG",  # type: ignore [arg-type]
        port=9090,
        pretty_print_logs=True,
        ssl_certfile=tmp_path / "custom_certfile",
        ssl_keyfile=tmp_path / "custom_keyfile",
    )

    assert config.bind_address == IPv4Address("192.168.52.52")
    assert config.log_directory is not None
    assert config.log_level == LogLevel.DEBUG
    assert config.port == 9090
    assert config.pretty_print_logs is True
    assert config.ssl_certfile is not None
    assert config.ssl_keyfile is not None


def test_tolerates_extras(tmp_path: Path):
    # This test validates that the ServiceConfiguration constructor does not
    # raise an error when it receives an unexpected (extra) parameter.
    ServiceConfiguration(extra_field="value")  # type: ignore [call-arg]
