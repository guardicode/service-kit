import uuid
from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.datastructures import Headers, State
from ulid import ULID

from service_kit.api import RequestID, RequestIDMiddleware
from service_kit.api.request_id_middleware import CORRELATION_ID_HEADER, REQUEST_ID_HEADER


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


def make_request(headers=None):
    request = MagicMock()
    request.headers = Headers(headers or {})
    request.state = State()
    return request


def _is_valid_id(value: RequestID) -> bool:
    if not isinstance(value, RequestID):
        return False

    with suppress(ValueError):
        uuid.UUID(value)
        return True

    with suppress(ValueError):
        ULID.from_str(value)
        return True

    return False


@pytest.mark.anyio
async def test_generates_request_id_when_header_absent():
    middleware = RequestIDMiddleware(app=MagicMock())
    request = make_request()

    await middleware.dispatch(request, AsyncMock())

    assert _is_valid_id(request.state.id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "request_id_header", [REQUEST_ID_HEADER, REQUEST_ID_HEADER.upper(), REQUEST_ID_HEADER.lower()]
)
async def test_uses_request_id_header_when_present(request_id_header: str):
    middleware = RequestIDMiddleware(app=MagicMock())
    request = make_request(headers={request_id_header: "client-provided-id"})

    await middleware.dispatch(request, AsyncMock())

    assert request.state.id == "client-provided-id"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "whitespace_request_id", [" ", "   ", "\n", "\t", "\n\t\t\n  ", "\t  \n", "\n  \t"]
)
async def test_whitespace_only_request_id(whitespace_request_id: RequestID):
    middleware = RequestIDMiddleware(app=MagicMock())
    request = make_request(headers={REQUEST_ID_HEADER: whitespace_request_id})

    await middleware.dispatch(request, AsyncMock())

    assert _is_valid_id(request.state.id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "correlation_id_header",
    [CORRELATION_ID_HEADER, CORRELATION_ID_HEADER.upper(), CORRELATION_ID_HEADER.lower()],
)
async def test_uses_correlation_id_header_when_present(correlation_id_header: str):
    middleware = RequestIDMiddleware(app=MagicMock())
    request = make_request(headers={correlation_id_header: "client-provided-id"})

    await middleware.dispatch(request, AsyncMock())

    assert request.state.correlation_id == "client-provided-id"


@pytest.mark.anyio
async def test_uses_correlation_id_is_None_when_header_absent():
    middleware = RequestIDMiddleware(app=MagicMock())
    request = make_request()

    await middleware.dispatch(request, AsyncMock())

    assert request.state.correlation_id is None
