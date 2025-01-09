from ipaddress import IPv4Address
from pathlib import Path
from typing import Annotated, Self

from pydantic import BeforeValidator, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from service_kit import BaseModel, NetworkPort
from service_kit.logging import LogLevel


class ServiceConfiguration(BaseSettings, BaseModel):
    model_config = SettingsConfigDict(env_parse_none_str="None", extra="ignore")

    bind_address: IPv4Address = Field(
        default=IPv4Address("127.0.0.1"), description="The interface to listen on"
    )
    debug: bool = Field(
        default=False, description="Enable debug mode (also override the log level)"
    )
    enable_hot_reload: bool = Field(
        default=False, description="Enable hot-reloading during development"
    )
    log_directory: Path | None = Field(
        default=None,
        description="The directory to write log files to (it will be created if it does not exist)",
    )
    log_level: Annotated[
        LogLevel, BeforeValidator(lambda v: v.upper() if isinstance(v, str) else v)
    ] = Field(default=LogLevel.INFO, description="The log level to use")
    port: NetworkPort = Field(default=NetworkPort(8080), description="The port to listen on")
    pretty_print_logs: bool = Field(default=True, description="Enable pretty-printing of JSON logs")
    ssl_certfile: Path | None = Field(
        default=None, description="The path to the SSL certificate file"
    )
    ssl_keyfile: Path | None = Field(default=None, description="The path to the SSL key file")

    @model_validator(mode="after")
    def override_log_level_on_debug(self) -> Self:
        if self.debug:
            original_frozen = self.model_config["frozen"]

            try:
                self.model_config["frozen"] = False
                self.log_level = LogLevel.TRACE
            finally:
                self.model_config["frozen"] = original_frozen

        return self
