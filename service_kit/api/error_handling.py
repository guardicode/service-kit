from http import HTTPStatus
from typing import Any, Callable, Type

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from service_kit.errors import StructuredError
from service_kit.logging import log_basic_error, log_structured_error

from . import APIResponse, InternalServerErrorResponse, UnauthorizedResponse


def register_authentication_error_handler(app: FastAPI):
    """,
    Registers an error handler to handle authentication errors

    NOTE: FastAPI raises 403 Forbidden in cases where 401 Unauthorized is the
    correct response. (see https://github.com/tiangolo/fastapi/issues/10177).
    Therefore, we're handling all 403 Forbidden errors and returning them as
    401 Unauthorized instead. This behavior is fine for single-user systems.
    It should be evaluated before use in multi-user systems.

    :param app: A FastAPI instance to register the handler for
    """

    @app.exception_handler(HTTPStatus.FORBIDDEN)
    @app.exception_handler(HTTPStatus.UNAUTHORIZED)
    async def handle_forbidden_error(request: Request, exc: HTTPStatus):
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content=UnauthorizedResponse(request_id=request.state.id).model_dump(),
        )


def register_timeout_error_handler(app: FastAPI):
    """
    Registers an error handler for catching TimeoutErrors

    :param app: A FastAPI instance to register the handler for
    """

    @app.exception_handler(TimeoutError)
    async def handle_timeout_error(request: Request, exc: TimeoutError):
        return handle_basic_error(
            request,
            exc,
            InternalServerErrorResponse,
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


async def default_error_handler_middleware(request: Request, call_next: Callable[[Request], Any]):
    """
    A middleware that handles any exception that gets raised by returning an
    Internal Server Error (500)
    """
    try:
        return await call_next(request)
    except StructuredError as err:
        return handle_structured_error(
            request, err, InternalServerErrorResponse, HTTPStatus.INTERNAL_SERVER_ERROR
        )
    except Exception as err:
        return handle_basic_error(
            request, err, InternalServerErrorResponse, HTTPStatus.INTERNAL_SERVER_ERROR
        )


def register_default_error_handler(app: FastAPI):
    """
    Registers the default error handler defined by the uncaught_exceptions_middleware

    NOTE: Adding a standard exception handler to catch unhandled exceptions
    does not function as intented. Instead, a middleware must be regisered to
    handle uncaught exceptions.
    Reference: https://stackoverflow.com/questions/61596911/catch-exception-globally-in-fastapi

    :param app: A FastAPI instance to register the handler for
    """
    app.middleware("http")(default_error_handler_middleware)


def handle_basic_error(
    request: Request,
    error: Exception,
    response_type: Type[APIResponse],
    status_code: HTTPStatus,
    message: str | None = None,
):
    log_basic_error(error)

    error_message = message if message else str(error)

    return JSONResponse(
        status_code=status_code,
        content=response_type(request_id=request.state.id, message=error_message).model_dump(),
    )


def handle_structured_error(
    request: Request,
    error: StructuredError,
    response_type: Type[APIResponse],
    status_code: HTTPStatus,
):
    log_structured_error(error)

    return JSONResponse(
        status_code=status_code,
        content=response_type(
            request_id=request.state.id,
            **error.structured_error,
        ).model_dump(mode="json", by_alias=True),
    )
