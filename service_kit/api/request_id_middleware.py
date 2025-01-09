from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ulid import ULID

from . import RequestID


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        request.state.id = self._generate_request_id()
        return await call_next(request)

    @staticmethod
    def _generate_request_id() -> RequestID:
        return str(ULID())
