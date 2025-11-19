def require_extra(extra_name: str, deps: list[str]) -> None:
    missing = []
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    if missing:
        raise ImportError(
            f"The '{extra_name}' extra is required in order to use '{__package__}'. "
            f"Install with:\n\n    pip install service-kit[{extra_name}]\n\n"
            f"Missing: {', '.join(missing)}"
        )


require_extra("api", ["fastapi", "ulid", "uvicorn"])

from .types import RequestID
from .responses import (
    APIResponse,
    BadRequestResponse,
    ConflictResponse,
    InternalServerErrorResponse,
    NotFoundResponse,
    TooManyRequestsResponse,
    UnauthorizedResponse,
    get_standard_responses,
)
from .error_handling import (
    default_error_handler_middleware,
    handle_basic_error,
    handle_structured_error,
    register_authentication_error_handler,
    register_timeout_error_handler,
    register_default_error_handler,
)
from .request_id_middleware import RequestIDMiddleware
from .request_log_middleware import RequestLogMiddleware
from .api_utils import bootstrap_logging, launch_uvicorn
