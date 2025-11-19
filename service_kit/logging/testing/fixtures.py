import pytest

from service_kit.logging import configure_logger


@pytest.fixture(autouse=True, scope="session")
def configure_test_logger(request):
    level = 0 if request.config.getoption("--show-logs") else 50000
    configure_logger(log_level=level, log_directory=None, pretty_print_logs=True)
