from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated, Final

from fastapi import Depends, FastAPI, Request

from service_kit.api import (
    RequestIDMiddleware,
    RequestLogMiddleware,
    bootstrap_logging,
    get_standard_responses,
    launch_uvicorn,
    register_authentication_error_handler,
    register_default_error_handler,
    register_timeout_error_handler,
)
from service_kit.configuration import ServiceConfiguration
from service_kit.logging import logger

PROJECT_NAME: Final[str] = "{{ project_name }}"
API_VERSION: Final[str] = "0.1.0"
ENTRYPOINT: Final[str] = (
    {% if package is not none %}  # noqa: E999
    "{{ package }}.{{ module }}:app"
    {% else %}
    "{{ module }}:app"
    {% endif %}
)

# NOTE: Objects that are shared between requests (like a database connection) must be
# declared globally, initialized in the setup() function, and cleaned up in the
# teardown() function. Some are passed to the path operation functions via
# FastAPI's dependency injection system, which can be overridden in the tests by
# setting app.dependency_overrides.
_some_dependency: None


def some_dependency() -> None:
    global _some_dependency

    if "_some_dependency" not in globals():
        _some_dependency = lambda: "some dependency"

    return _some_dependency


def load_configuration():
    # REPLACE WITH A CUSTOM SUBCLASS OF ServiceConfiguration.
    return ServiceConfiguration()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    config = await setup(_app)
    yield
    await teardown(_app, config)


async def setup(_app: FastAPI) -> ServiceConfiguration:
    global _some_dependency

    # Uvicorn forks the process, so we need to reload the configuration here.
    config = load_configuration()
    logger.critical(config)
    await bootstrap_logging(_app, config)

    _some_dependency = None
    ...

    return config


async def teardown(_app: FastAPI, config: ServiceConfiguration):
    logger.info(f"Shutting down {PROJECT_NAME}...")
    ...


def register_error_handlers(_app: FastAPI):
    register_authentication_error_handler(app)
    register_timeout_error_handler(app)
    register_default_error_handler(app)


app = FastAPI(
    lifespan=lifespan,
    title=PROJECT_NAME,
    version=API_VERSION,
    dependencies=[],
    responses=get_standard_responses([HTTPStatus.UNAUTHORIZED]),
)
# NOTE: Error handlers must be registered before the RequestLogMiddleware, otherwise responses to
#       queries that raise unexpected/uncaught exceptions will not be properly logged.
register_error_handlers(app)

# Middlewares are executed in the reverse order in which they are added.
app.add_middleware(RequestLogMiddleware)
app.add_middleware(RequestIDMiddleware)


{% if endpoints is not none %}
{{ endpoints }}
{% else %}
@app.post(
    "/echo/{customer_id}",
    summary="An example endpoint that responds with the specified Customer ID",
    responses={
        **get_standard_responses(
            [
                HTTPStatus.BAD_REQUEST,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                HTTPStatus.NOT_FOUND,
            ]
        )
    },
    status_code=HTTPStatus.CREATED,
)
async def example(
    _some_dependency: Annotated[None, Depends(some_dependency)],
    customer_id: str,
    request: Request,
) -> str:
    """
    Example endpoint
    """
    # SECURITY: The customer_id is used to authenticate the user and authorize
    # the request. Endpoints must not allow the customer ID to be included in
    # the request body. If the customer ID were included in the request body,
    # it could lead to a bypass of the authorization check.

    # Do something
    ...

    return customer_id
{% endif %}


def main():
    launch_uvicorn(PROJECT_NAME, ENTRYPOINT, load_configuration())


if __name__ == "__main__":
    main()
