import json

from fastapi import Request, Response
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware

from service_kit.logging import logger


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
        common_request_fields = {
            "method": request.method,
            "path": request.url.path,
            "query_parameters": dict(request.query_params),
            "source": request.client._asdict() if request.client is not None else None,
            "url": str(request.url),
        }

        sanitized_headers = RequestLogMiddleware.sanitize_headers(request.headers)

        if cls.debug:
            try:
                request_body = await request.json()
            except json.JSONDecodeError:
                request_body = str(await request.body())

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
