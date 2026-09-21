import re
from typing import Callable, Final

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from service_kit.logging import SecurityRisk, logger

from . import RequestID

REQUEST_ID_HEADER: Final[str] = "x-request-id"
CORRELATION_ID_HEADER: Final[str] = "x-correlation-id"

_SAFE_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9_-]+$")

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
        request_id_from_header = self._safe_retrieve_header(request, REQUEST_ID_HEADER)
        correlation_id_from_header = self._safe_retrieve_header(request, CORRELATION_ID_HEADER)

        request.state.id = (
            request_id_from_header if request_id_from_header else self._generate_request_id()
        )
        request.state.correlation_id = correlation_id_from_header

        return await call_next(request)

    @staticmethod
    def _safe_retrieve_header(request: Request, header: str) -> str | None:
        value_from_header = request.headers.get(header)

        if value_from_header is None:
            return None

        value_from_header = value_from_header.strip()

        if not value_from_header:
            return None

        if not _SAFE_ID_RE.match(value_from_header):
            logger.warning(
                (
                    "A header containing illegal characters was received. "
                    "This may indicate a log injection attack."
                ),
                security_risk=SecurityRisk.LOW,
                header=header,
                # Logging the value is safe because the logger escapes unsafe characters when
                # serializing to JSON
                value=value_from_header,
            )

            return None

        return value_from_header

    @staticmethod
    def _generate_request_id() -> RequestID:
        return _generate_id()
