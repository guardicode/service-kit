from typing import Final

import pytest

from service_kit.api import RequestID

TEST_REQUEST_ID: Final[str] = "test_request_id"


@pytest.fixture
def request_id(monkeypatch: pytest.MonkeyPatch) -> RequestID:
    monkeypatch.setattr(
        "service_kit.api.RequestIDMiddleware._generate_request_id",
        lambda *args, **kwargs: TEST_REQUEST_ID,
    )

    return TEST_REQUEST_ID
