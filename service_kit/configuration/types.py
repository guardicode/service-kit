from typing import Annotated, TypeVar

from pydantic.functional_validators import AfterValidator, BeforeValidator

from . import coerce_to_tuple, parse_comma_separated_sequence

T = TypeVar("T")
# This type definition is a workaround (read, "hack") to allow
# pydantic-settings to parse a broader range of inputs as a list of strings. If
# either `tuple[str]` or `list[str]` is used by itself, pydantic-settings will
# not accept a list like "a,b,c". Instead, the input must be JSON, like
# '["a", "b", "c"]'. However, when using a union, pydantic-settings will accept
# either the simple/lazy commma-separated string or the JSON array.
ListConfigurationType = Annotated[
    tuple[T] | list[T],
    BeforeValidator(parse_comma_separated_sequence),
    AfterValidator(coerce_to_tuple),
]
