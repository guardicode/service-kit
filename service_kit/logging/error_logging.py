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


try:
    import psycopg

    def log_postgres_error(err: psycopg.Error):
        logger.error(
            "A PostgreSQL error occurred",
            postgres_error_message=str(err),
            **_format_postgres_error_diagnostics(err),
        )

    def _format_postgres_error_diagnostics(err: psycopg.Error) -> dict[str, str]:
        diagnostic_fields = {
            "column_name": err.diag.column_name,
            "constraint_name": err.diag.constraint_name,
            "context": err.diag.context,
            "datatype_name": err.diag.datatype_name,
            "internal_position": err.diag.internal_position,
            "internal_query": err.diag.internal_query,
            "message_detail": err.diag.message_detail,
            "message_hint": err.diag.message_hint,
            "message_primary": err.diag.message_primary,
            "schema_name": err.diag.schema_name,
            "severity": err.diag.severity,
            "severity_nonlocalized": err.diag.severity_nonlocalized,
            "source_file": err.diag.source_file,
            "source_function": err.diag.source_function,
            "source_line": err.diag.source_line,
            "sqlstate": err.diag.sqlstate,
            "statement_position": err.diag.statement_position,
            "table_name": err.diag.table_name,
        }

        return {k: v for k, v in diagnostic_fields.items() if v is not None}

except ImportError:

    def log_postgres_error(err):
        raise RuntimeError(
            "log_postrges_error() was called but psycopg could not be imported. Please ensure"
            "ServiceKit is installed with the [psycopg] extra:"
            "`service-kit = {"
            'git = "ssh://git@github.com/guardicode/service-kit.git", extras = ["psycopg"]'
            "}`"
        )
