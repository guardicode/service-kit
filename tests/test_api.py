from http import HTTPStatus

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from service_kit.api import (
    RequestID,
    RequestIDMiddleware,
    RequestLogMiddleware,
    register_authentication_error_handler,
    register_default_error_handler,
    register_timeout_error_handler,
)
from service_kit.errors import StructuredError


def register_error_handlers(_app: FastAPI):
    register_authentication_error_handler(app)
    register_timeout_error_handler(app)
    register_default_error_handler(app)


app = FastAPI()
# NOTE: Error handlers must be registered before the RequestLogMiddleware, otherwise responses to
#       queries that raise unexpected/uncaught exceptions will not be properly logged.
register_error_handlers(app)

# Middlewares are executed in the reverse order in which they are added.
app.add_middleware(RequestLogMiddleware)
app.add_middleware(RequestIDMiddleware)


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def async_api_client() -> AsyncClient:
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


TEST_EXCEPTION_MESSAGE = "This is a test exception"


@app.get("/exception-500")
def exception_500_test_endpoint():
    raise ValueError(TEST_EXCEPTION_MESSAGE)


def test_500_error_on_exception(api_client: TestClient, request_id: RequestID):
    response = api_client.get("/exception-500")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["message"] == TEST_EXCEPTION_MESSAGE
    assert response.json()["request_id"] == request_id
    assert response.headers["content-type"] == "application/json"


@app.get("/timeout-500")
def timeout_500_test_endpoint():
    raise TimeoutError(TEST_EXCEPTION_MESSAGE)


def test_500_error_on_timeout(api_client: TestClient, request_id: RequestID):
    response = api_client.get("/timeout-500")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert TEST_EXCEPTION_MESSAGE not in response.json()["message"]
    assert response.json()["request_id"] == request_id
    assert response.headers["content-type"] == "application/json"


@app.get("/structured-error")
def exception_structured_error():
    raise StructuredError(TEST_EXCEPTION_MESSAGE, param1="p1", param2="p2")


def test_structured_error(api_client: TestClient, request_id: RequestID):
    expected_error = {
        "request_id": request_id,
        "message": TEST_EXCEPTION_MESSAGE,
        "param1": "p1",
        "param2": "p2",
    }

    response = api_client.get("/structured-error")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json() == expected_error
    assert response.headers["content-type"] == "application/json"


@app.get("/structured-error-2")
def exception_structured_error_2():
    raise StructuredError(TEST_EXCEPTION_MESSAGE)


def test_structured_error_handling__no_additional_properties(
    api_client: TestClient, request_id: RequestID
):
    expected_error = {
        "request_id": request_id,
        "message": TEST_EXCEPTION_MESSAGE,
    }

    response = api_client.get("/structured-error-2")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json() == expected_error
    assert response.headers["content-type"] == "application/json"
