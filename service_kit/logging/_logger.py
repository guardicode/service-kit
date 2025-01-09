from __future__ import annotations

import inspect
import json
import logging
import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import loguru
from loguru import logger as _logger
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import JsonLexer

from service_kit import BaseModel

from . import LogLevel


class InterceptHandler(logging.Handler):
    # Reroutes messages for Python's logging library to Loguru.
    # This is useful for catching the log messages from third-party libraries.
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Serializer:
    def __init__(self, colorize: bool):
        self._indent: int | None = None
        self._colorize = colorize
        self._lexer = JsonLexer()
        self._formatter = TerminalTrueColorFormatter(style="rrt")

    def set_pretty_print(self, pretty_print_logs: bool):
        # A separate method to set this is needed as this option is not configured until after the
        # configuration file has been read, which is also after the logger has been imported.
        self._indent = 4 if pretty_print_logs else None

    def __call__(self, record: loguru.Record):
        subset = {
            "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S:%f %z"),
            "level": record["level"].name,
            "module": record["module"],
            "file": record["file"].path,
            "function": record["function"],
            "message": record["message"],
            **record["extra"],
        }
        json_str = self._serialize_json(subset)

        record["extra"]["serialized"] = json_str
        record["extra"]["colorized"] = self._colorize_json(json_str) if self._colorize else json_str

    def _colorize_json(self, json_str: str) -> str:
        return highlight(json_str, self._lexer, self._formatter)

    def _serialize_json(self, subset: dict[str, Any]) -> str:
        return json.dumps(
            subset, indent=self._indent, sort_keys=True, default=self._default_serializer
        )

    @staticmethod
    def _default_serializer(obj: Any) -> str | dict[str, Any]:
        if isinstance(obj, BaseModel):
            return obj.to_json_dict()

        return str(obj)


io_stream = sys.stderr
serializer = Serializer(io_stream.isatty())

# The logger has to be patched before it's imported by anything else, otherwise
# the importing module won't have access to the patched logger.
logger = _logger.patch(serializer)


def configure_logger(
    log_level: LogLevel | int,
    log_directory: Path | None,
    pretty_print_logs: bool,
    log_file_prefix: str | None = None,
):
    """
    Configures the service's structured logger

    :param log_level: The minimum severity level to log messages for
    :param log_directory: An optional directory where log files will be stored. If this is None
                         (the default), then no log files will be written. If the specified
                         directory does not exist it will be created.
    :param pretty_print_logs: Whether or not to pretty-print logs
    :param log_file_prefix: A string that will be prepended to any log files
                            that are created (default: None)
    """
    serializer.set_pretty_print(pretty_print_logs)

    # Remove default logger before adding new handlers.
    logger.remove()

    logger.add(
        io_stream,
        level=log_level,
        backtrace=True,
        diagnose=False,  # For security purposes, this should be set to False in production
        format="{extra[colorized]}",
    )

    if log_directory is not None:
        _create_log_directory(log_directory)

        log_file_name_template = "{time}.log"
        if log_file_prefix is not None:
            log_file_name_template = f"{log_file_prefix}_{log_file_name_template}"

        logger.add(
            log_directory / log_file_name_template,
            rotation="00:00",
            level=log_level,
            backtrace=True,
            diagnose=False,  # For security purposes, this should be set to False in production
            format="{extra[serialized]}",
            opener=lambda path, flags: os.open(path, flags, 0o600),
        )

    intercept_preconfigured_loggers(("uvicorn", "uvicorn.access", "uvicorn.asgi", "uvicorn.error"))


def _create_log_directory(log_directory: Path):
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    elif not log_directory.is_dir():
        raise ValueError(f"{log_directory} is not a directory")


def intercept_preconfigured_loggers(logger_names: Iterable[str]):
    """
    Configure 3rd-party packages to use the correct logger

    Some 3rd-party packages configure their own loggers. For example, uvicorn forks and configures
    logging. As a result, its loggers need to be intercepted in order to capture the package's log
    messages in all of our sinks and in our desired format.

    :param logger_names: An iterable of names of the loggers that must be intercepted
    """
    intercept_handler = InterceptHandler()

    logging.basicConfig(handlers=[intercept_handler], level=0, force=True)

    for name in logger_names:
        third_party_logger = logging.getLogger(name)
        third_party_logger.handlers = [intercept_handler]
        third_party_logger.propagate = False
        third_party_logger.propagate = False
