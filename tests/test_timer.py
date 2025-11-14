from unittest.mock import MagicMock

import pytest
from loguru._logger import Logger

from service_kit.utils import Timer


@pytest.fixture
def mock_logger():
    return MagicMock(spec=Logger)


def test_timer_context_manager(mock_logger: Logger):
    pc = [0.1]

    def fake_perf_counter():
        return pc[0]

    with Timer("test action", logger=mock_logger, get_time=fake_perf_counter):
        pc[0] += 0.1  # Simulate 0.1 seconds passing

    mock_logger.debug.assert_called_once_with(
        "Timer finished",
        action="test action",
        time_taken_in_seconds=pytest.approx(0.1, rel=1e-6),
    )


def test_timer_decorator(mock_logger: Logger):
    pc = [0.1]

    def fake_perf_counter():
        return pc[0]

    @Timer("test function", logger=mock_logger, get_time=fake_perf_counter)
    def sample_function():
        pc[0] += 0.2  # Simulate 0.2 seconds passing

    sample_function()

    mock_logger.debug.assert_called_once_with(
        "Timer finished",
        action="test function",
        time_taken_in_seconds=pytest.approx(0.2, rel=1e-6),
    )
