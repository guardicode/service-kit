# Loguru define its types in stub files so we need this import to be able to use them.
from __future__ import annotations

import time
from typing import Any, Callable

import loguru

from service_kit.logging import logger as service_kit_logger


class Timer:
    """
    A utility for timing how long something took.

    Example:
       Context manager usage:
         with Timer("some action"):
             do_something()

       Output:
         "Timer finished", action="some action", time_taken_in_seconds=0.12345

       Decorator usage:
       @Timer("some function")
       def some_function():
         return do_something()

       do_something()

       Output:
         "Timer finished", action="some function", time_taken_in_seconds=0.12345
    """

    def __init__(
        self,
        action: str,
        get_time: Callable[[], float] = time.perf_counter,
        logger: loguru.Logger = service_kit_logger,
    ):
        self._get_time = get_time
        self._action = action
        self._logger = logger

    def __enter__(self):
        self._start = self._get_time()
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self._elapsed = self._get_time() - self._start

        self._log_elapsed(self._elapsed)

    def __call__(self, fn: Callable):
        def _inner(*args, **kwargs) -> Any:
            start = self._get_time()
            return_value = fn(*args, **kwargs)
            elapsed = self._get_time() - start
            self._log_elapsed(elapsed)

            return return_value

        return _inner

    def _log_elapsed(self, elapsed: float) -> None:
        self._logger.debug(  # type: ignore[call-arg]
            "Timer finished", action=self._action, time_taken_in_seconds=elapsed
        )
