import pytest

from service_kit.logging.testing import run_configure_test_logger


# ServiceKit actually tests the logger itself, so the test logger is scoped per-module to avoid the
# the logger tests impacting the logger in unrelated tests.
@pytest.fixture(autouse=True, scope="module")
def configure_test_logger(request):
    run_configure_test_logger(request)
