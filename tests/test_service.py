import subprocess
import sys
import time
import warnings
from http import HTTPStatus
from pathlib import Path
from typing import Final

import jinja2
import pytest
import requests

pytestmark = pytest.mark.slow

UNEXPECTED_ERROR_MESSAGE: Final[str] = "Unexpected error"
TEST_SERVICE_FILE_NAME: Final[Path] = Path("integration_test.py")
ENDPOINT: Final[str] = (
    """
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
    if customer_id == "timeout":
        raise TimeoutError("Test Timout Error")

    if customer_id == "error":
        raise ValueError(\""""
    + UNEXPECTED_ERROR_MESSAGE
    + """\")

    return customer_id
"""
)
ENDPOINT_URL: Final[str] = "http://127.0.0.1:8080/echo"


@pytest.fixture(scope="module", autouse=True)
def start_service(tmpdir_factory: pytest.TempdirFactory):
    tmp_dir = tmpdir_factory.mktemp("integration-tests")

    test_service = build_service(tmp_dir)

    with open(tmp_dir / TEST_SERVICE_FILE_NAME, "w") as f:
        f.write(test_service)

    server_process = subprocess.Popen(
        [sys.executable, TEST_SERVICE_FILE_NAME],
        cwd=tmp_dir,
        # Redirecting to /dev/null only partially works, since uvicorn may not
        # respect this when it forks the child process
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)  # Wait for the server to fully boot

    yield

    try:
        server_process.terminate()
        server_process.wait(5)
    except subprocess.TimeoutExpired:
        warnings.warn("The server did not shutdown gracefully")
        server_process.kill()


def build_service(tmp_dir: Path):
    environment = jinja2.Environment()

    with open(Path(__file__).parent.parent / "template_service.py", "r") as f:
        template = environment.from_string(f.read())

    return template.render(
        endpoints=ENDPOINT,
        module=TEST_SERVICE_FILE_NAME.stem,
        package=None,
        project_name="integration test",
    )


def test_service_success():
    test_input = "test-string"

    response = requests.post(f"{ENDPOINT_URL}/{test_input}")

    assert response.ok
    assert response.json() == test_input


def test_service_timeout(request_id: str):

    response = requests.post(f"{ENDPOINT_URL}/timeout")

    assert not response.ok
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["request_id"] is not None
    assert "timed out" in response.json()["message"]


def test_service_unexpected_error(request_id: str):

    response = requests.post(f"{ENDPOINT_URL}/error")

    assert not response.ok
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["request_id"] is not None
    assert response.json()["message"] == UNEXPECTED_ERROR_MESSAGE
