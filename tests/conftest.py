from collections.abc import Iterable, Sequence

import pytest
from service_kit.logging import configure_logger


def pytest_addoption(parser):
    parser.addoption(
        "--show-logs",
        action="store_true",
        default=False,
        help="Show log messages",
    )

    parser.addoption(
        "--skip-db",
        action="store_true",
        default=False,
        help="Skip tests that require a database",
    )

    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="Skip long-running tests (implies --skip-db)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "db: mark test as requiring a database")


def pytest_collection_modifyitems(config: pytest.Config, items: Sequence[pytest.Function]):
    if config.getoption("--skip-db"):
        _mark_skipped_db(items)

    if config.getoption("--skip-slow"):
        _mark_skipped_slow(items)
        _mark_skipped_db(items)


def _mark_skipped_db(items: Iterable[pytest.Function]):
    skip_db = pytest.mark.skip(reason="Skipped because --skip-db was set")
    _mark_skipped_tests("db", skip_db, items)


def _mark_skipped_slow(items: Iterable[pytest.Function]):
    skip_slow = pytest.mark.skip(reason="skipping long-running tests")
    _mark_skipped_tests("slow", skip_slow, items)


def _mark_skipped_tests(
    keyword: str, marker: pytest.MarkDecorator, items: Iterable[pytest.Function]
):
    for item in items:
        if keyword in item.keywords:
            item.add_marker(marker)


@pytest.fixture(autouse=True, scope="session")
def configure_test_logger(request):
    level = 0 if request.config.getoption("--show-logs") else 50000
    configure_logger(log_level=level, log_directory=None, pretty_print_logs=True)
