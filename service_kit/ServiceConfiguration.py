from pathlib import Path
from typing import Protocol

from .logging import LogLevel


class ServiceConfiguration(Protocol):
    @property
    def log_directory(self) -> Path: ...

    @property
    def log_level(self) -> LogLevel: ...

    @property
    def pretty_print_logs(self) -> bool: ...
