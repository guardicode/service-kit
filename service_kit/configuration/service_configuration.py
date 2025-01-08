from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings

from service_kit import BaseModel
from service_kit.logging import LogLevel


class ServiceConfiguration(BaseSettings, BaseModel):
    debug: bool
    log_directory: Path | None
    log_level: LogLevel
    pretty_print_logs: bool

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
