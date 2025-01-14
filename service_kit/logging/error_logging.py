import traceback
from typing import Any

from service_kit.errors import StructuredError

from . import LogLevel, logger


def log_exception_group(
    group: ExceptionGroup,
    *,
    log_level: LogLevel = LogLevel.ERROR,
    message: str = "An unexpected error occurred",
):
    for err in group.exceptions:
        if isinstance(err, StructuredError):
            log_structured_error(err, log_level=log_level, message=message)
        else:
            log_basic_error(err, log_level=log_level, message=message)


def log_basic_error(
    error: Exception,
    *,
    log_level: LogLevel = LogLevel.ERROR,
    message: str = "An unexpected error occurred",
    **kwargs: Any,
):
    """
    Log a basic (non-structured) error

    :param error: An error to log
    :param log_level: The log level to use (default: "ERROR")
    :message: The message to log (default: "An unexpected error occurred")
    :param kwargs: Additional attributes to include in the log entry
    """
    logger.log(
        log_level,
        message,
        error=str(error),
        error_type=error.__class__.__name__,
        traceback=traceback.format_exc(),
        **kwargs,
    )


def log_structured_error(
    error: StructuredError,
    *,
    log_level: LogLevel = LogLevel.ERROR,
    message: str = "An unexpected error occurred",
    **kwargs: Any,
):
    """
    Log a structured error

    :param error: A structured error to log
    :param log_level: The log level to use (default: "ERROR")
    :message: The message to log (default: "An unexpected error occurred")
    :param kwargs: Additional attributes to include in the log entry
    """

    # "message" is a preexisting, positional parameter in logger.error().
    # Replacing error.structured_error["message"] with ["error"].
    structured_error = error.structured_error
    structured_error["error"] = structured_error.pop("message", None)

    logger.log(
        log_level,
        message,
        **structured_error,
        error_type=error.__class__.__name__,
        traceback=traceback.format_exc(),
        **kwargs,
    )
