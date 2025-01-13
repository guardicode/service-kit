from typing import Any

from monkeytypes import InfectionMonkeyBaseModel
from monkeytypes import MutableInfectionMonkeyModelConfig as MutableModelConfig
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError


class ServiceKitBaseModel(InfectionMonkeyBaseModel):
    def __setattr__(self, name: str, value: Any):
        # This method overrides InfectionMonkeyBaseModel.__setattr__().
        #  See the comments in _raise_type_or_value_error() for more details.
        PydanticBaseModel.__setattr__(self, name, value)

    @staticmethod
    def _raise_type_or_value_error(error: ValidationError):
        # This method overrides InfectionMonkeyBaseModel._raise_type_or_value_error(). Ideally, the
        # components in this repository that use BaseModel subclasses would be decoupled
        # from pydantic. This allows as much code as possible to remain pydantic-agnostic and be
        # insulated from changes in design or API (e.g. switching from Pydantic v1 to v2 or
        # abandoning Pydantic altogether). This includes insulating our components from Pydantic's
        # ValidationError (see
        # https://github.com/guardicode/monkeytypes/blob/95c0c9784b86b48562b6afd0ab7c4d078f66182d/monkeytypes/base_models.py#L35-L53  # noqa: E501
        # for more details.
        #
        # FastAPI is tightly coupled to Pydantic, and this coupling provides a lot of value. One
        # benefit is the fantastic error descriptions that FastAPI provides to users when invalid
        # data is sent to an endpoint. In order for this functionality to behave properly, our
        # models need to raise Pydantic's ValidationError. Therefore, in order to maximize value
        # from FastAPI, we need to expose pydantic.ValidationError to our components.
        #
        # Because InfectionMonkeyBaseModel provides some methods used for serialization that
        # insulate our components from Pydantic, there's still value in subclassing it but
        # overriding this method.

        raise error


class MutableServiceKitBaseModel(ServiceKitBaseModel):
    model_config = MutableModelConfig
