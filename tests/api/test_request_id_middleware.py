import uuid
from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.datastructures import Headers, State
from ulid import ULID

from service_kit.api import RequestID, RequestIDMiddleware


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
async def test_adds_request_id_to_state():
    middleware = RequestIDMiddleware(app=MagicMock())
    request = make_request()

    await middleware.dispatch(request, AsyncMock())

    assert _is_valid_id(request.state.id)
