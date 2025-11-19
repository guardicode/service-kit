from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import loguru
import pytest

from service_kit.utils import Timer


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock(spec=loguru._logger.Logger)


def test_timer_context_manager(mock_logger: loguru.Logger):
    pc = 1

    def fake_perf_counter():
        return pc

    with Timer("test action", logger=mock_logger, get_time=fake_perf_counter):
        pc += 1  # Simulate 1 second passing

    mock_logger.debug.assert_called_once_with(
        "Timer finished",
        action="test action",
        time_taken_in_seconds=1,
    )


def test_timer_decorator(mock_logger: loguru.Logger):
    pc = SimpleNamespace(value=1)

    def fake_perf_counter():
        return pc.value

    @Timer("test function", logger=mock_logger, get_time=fake_perf_counter)
    def sample_function():
        pc.value += 2  # Simulate 2 seconds passing

    sample_function()

    mock_logger.debug.assert_called_once_with(
        "Timer finished",
        action="test function",
        time_taken_in_seconds=2,
    )
