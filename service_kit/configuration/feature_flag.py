from typing import Self

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class FeatureFlag:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        from_bool_schema = core_schema.no_info_after_validator_function(
            cls.from_bool,
            handler(bool),
        )

        return core_schema.json_or_python_schema(
            json_schema=from_bool_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    from_bool_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.enabled
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema["examples"] = ["true", "True", "False", "false", "1", "0"]
        return json_schema

    @classmethod
    def from_bool(cls, value: bool) -> Self:
        return cls(enabled=value)

    def __eq__(self, other):
        if not isinstance(other, FeatureFlag):
            return False
        return self.enabled == other.enabled
