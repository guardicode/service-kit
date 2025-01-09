from pathlib import Path

import uvicorn
from fastapi import FastAPI

from service_kit.configuration import ServiceConfiguration
from service_kit.logging import RequestLogMiddleware, SecurityRisk, configure_logger, logger


async def bootstrap_logging(app: FastAPI, config: ServiceConfiguration):
    """
    Configures the logger and log-related middleware for the API

    :param app: The server's FastAPI instance
    :param config: The server's configuration
    """
    configure_logger(config.log_level, config.log_directory, config.pretty_print_logs)
    logger.info("Logger configured.")
    logger.info("Current configuration", **config.to_json_dict())

    if config.debug:
        logger.warning(
            (
                "Debug mode is enabled. This may lead to sensitive information being logged or "
                "returned to the API callers. Do not enable debug mode in production."
            ),
            security_risk=SecurityRisk.MEDIUM,
        )

    RequestLogMiddleware.debug = config.debug


def launch_uvicorn(project_name: str, entrypoint: str, config: ServiceConfiguration):
    """
    Launch the uvicorn server

    :param project_name: The name of the project, used primarily for logging
    :param entrypoint: A string to pass to uvicorn that defines the entrypoint.
                       Example: "my_package.my_module.app"
    :param config: The server's configuration
    """
    logger.info(f"Starting {project_name}...")
    uvicorn.run(
        entrypoint,
        host=str(config.bind_address),
        port=config.port,
        reload=config.enable_hot_reload,
        ssl_keyfile=_get_path_str(config.ssl_keyfile),
        ssl_certfile=_get_path_str(config.ssl_certfile),
    )


def _get_path_str(path: Path | None) -> str | None:
    if path:
        return str(path)

    return None
