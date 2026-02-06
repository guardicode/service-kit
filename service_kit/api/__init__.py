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

from .types import RequestID as RequestID
from .responses import (
    APIResponse as APIResponse,
    BadRequestResponse as BadRequestResponse,
    ConflictResponse as ConflictResponse,
    InternalServerErrorResponse as InternalServerErrorResponse,
    NotFoundResponse as NotFoundResponse,
    TooManyRequestsResponse as TooManyRequestsResponse,
    UnauthorizedResponse as UnauthorizedResponse,
    get_standard_responses as get_standard_responses,
)
from .error_handling import (
    default_error_handler_middleware as default_error_handler_middleware,
    handle_basic_error as handle_basic_error,
    handle_structured_error as handle_structured_error,
    register_authentication_error_handler as register_authentication_error_handler,
    register_timeout_error_handler as register_timeout_error_handler,
    register_default_error_handler as register_default_error_handler,
)
from .request_id_middleware import RequestIDMiddleware as RequestIDMiddleware
from .request_log_middleware import RequestLogMiddleware as RequestLogMiddleware
from .api_utils import bootstrap_logging, launch_uvicorn as launch_uvicorn
