from __future__ import annotations

import inspect
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import loguru
from fastapi import Request, Response
from loguru import logger as _logger
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import JsonLexer
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware

from service_kit import BaseModel

from . import LogLevel


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


class RequestLogMiddleware(BaseHTTPMiddleware):
    debug: bool = False

    async def dispatch(self, request, call_next):
        with logger.contextualize(request_id=request.state.id):
            await RequestLogMiddleware.log_request(request)
            response = await call_next(request)
            await RequestLogMiddleware.log_response(response)

        return response

    @classmethod
    async def log_request(cls, request: Request) -> None:
        try:
            request_body = await request.json()
        except json.JSONDecodeError:
            request_body = str(await request.body())

        common_request_fields = {
            "method": request.method,
            "path": request.url.path,
            "query_parameters": dict(request.query_params),
            "source": request.client._asdict() if request.client is not None else None,
            "url": str(request.url),
        }

        sanitized_headers = RequestLogMiddleware.sanitize_headers(request.headers)

        if cls.debug:
            logger.debug(
                "Request received",
                **common_request_fields,
                headers=sanitized_headers,
                body=request_body,
            )
        logger.info("Request received", **common_request_fields)

    @staticmethod
    def sanitize_headers(headers: Headers) -> dict[str, str]:
        sanitized_headers = {}

        for k, v in headers.items():
            if k.lower() == "authorization":
                sanitized_headers[k] = "********"
            else:
                sanitized_headers[k] = v

        return sanitized_headers

    @classmethod
    async def log_response(cls, response: Response):
        if cls.debug:
            logger.debug(
                "Sending response",
                headers=dict(response.headers),
                status_code=response.status_code,
            )
        logger.info("Sending reponse", status_code=response.status_code)


def configure_logger(
    log_level: LogLevel | int,
    log_directory: Path | None,
    pretty_print_logs: bool,
    log_file_prefix: str | None = None,
):
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

    intercept_preconfigured_loggers()


def intercept_preconfigured_loggers():
    # Since uvicorn forks and configures logging, we need to incercept its
    # loggers in order to capture them in all of our sinks and in our desired
    # format.
    intercept_handler = InterceptHandler()

    logging.basicConfig(handlers=[intercept_handler], level=0, force=True)

    for name in ("uvicorn", "uvicorn.access", "uvicorn.asgi", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = [intercept_handler]
        uvicorn_logger.propagate = False
        uvicorn_logger.propagate = False
