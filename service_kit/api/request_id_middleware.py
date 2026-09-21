from typing import Callable, Final

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from . import RequestID

REQUEST_ID_HEADER: Final[str] = "x-request-id"
CORRELATION_ID_HEADER: Final[str] = "x-correlation-id"

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
    """Middleware that assigns a unique request ID and optional correlation ID to each request.

    Reads the ``x-request-id`` header if present; otherwise generates a new time-ordered ID
    (UUIDv7 on Python 3.14+, ULID on earlier versions) and stores it in ``request.state.id``.

    Reads the ``x-correlation-id`` header if present and stores it in
    ``request.state.correlation_id``; otherwise sets that attribute to ``None``.

    This middleware must run before :class:`RequestLogMiddleware` so that the log context
    can reference both IDs.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        request_id_from_header = request.headers.get(REQUEST_ID_HEADER, "").strip()
        correlation_id_from_header = request.headers.get(CORRELATION_ID_HEADER, "").strip()

        # Note that neither the request ID nor the correlation ID may be empty strings.
        if request_id_from_header:
            request.state.id = request_id_from_header
        else:
            request.state.id = self._generate_request_id()

        if correlation_id_from_header:
            request.state.correlation_id = correlation_id_from_header
        else:
            request.state.correlation_id = None

        return await call_next(request)

    @staticmethod
    def _generate_request_id() -> RequestID:
        return _generate_id()
