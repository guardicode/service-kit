from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from . import RequestID

try:
    # UUIDv7 is available in Python 3.14+ and should be preferred over ULID
    from uuid import uuid7  # type: ignore [attr-defined]

    def _generate_id() -> str:
        return str(uuid7())

except ImportError:
    # Consider requiring Python 3.14+ in Service-Kit v3 and removing ULID as a
    # dependency
    from ulid import ULID

    def _generate_id() -> str:
        return str(ULID())


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        request.state.id = self._generate_request_id()
        return await call_next(request)

    @staticmethod
    def _generate_request_id() -> RequestID:
        return _generate_id()
