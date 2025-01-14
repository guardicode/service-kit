from collections.abc import Iterable
from http import HTTPStatus
from typing import Annotated, Any, Type

from pydantic import BaseModel, ConfigDict, Field

from . import RequestID


class APIResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    request_id: RequestID
    message: str


class BadRequestResponse(APIResponse):
    message: Annotated[str, Field(examples=["Request was malformed."])]


class ConflictResponse(APIResponse):
    message: Annotated[
        str, Field(examples=["This request conflicts with the server-side state of the resource."])
    ]


class InternalServerErrorResponse(APIResponse):
    message: Annotated[str, Field(examples=["An internal server error occurred."])]


class NotFoundResponse(APIResponse):
    message: Annotated[str, Field(examples=["Requested resource was not found."])]


class TooManyRequestsResponse(APIResponse):
    message: Annotated[str, Field(examples=["Too many requests were made."])]


class UnauthorizedResponse(APIResponse):
    message: Annotated[str, Field(examples=["The bearer token was missing or incorrect."])] = (
        "The bearer token was missing or incorrect."
    )


_standard_responses: dict[HTTPStatus, dict[str, Type[BaseModel] | dict]] = {
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "content": {"application/json": {"schema": InternalServerErrorResponse.model_json_schema()}}
    },
    HTTPStatus.BAD_REQUEST: {
        "content": {"application/json": {"schema": BadRequestResponse.model_json_schema()}}
    },
    HTTPStatus.CONFLICT: {
        "content": {"application/json": {"schema": ConflictResponse.model_json_schema()}}
    },
    HTTPStatus.NOT_FOUND: {
        "content": {"application/json": {"schema": NotFoundResponse.model_json_schema()}}
    },
    HTTPStatus.TOO_MANY_REQUESTS: {
        "content": {"application/json": {"schema": TooManyRequestsResponse.model_json_schema()}}
    },
    HTTPStatus.UNAUTHORIZED: {
        "content": {"application/json": {"schema": UnauthorizedResponse.model_json_schema()}}
    },
}


def get_standard_responses(statuses: Iterable[HTTPStatus]) -> dict[int | str, dict[str, Any]]:
    return {int(status): _standard_responses[status] for status in statuses}
