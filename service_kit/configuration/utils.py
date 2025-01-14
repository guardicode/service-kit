from collections.abc import Sequence
from typing import Any


def parse_comma_separated_sequence(value: Any) -> Sequence[str]:
    if isinstance(value, str):
        return tuple(v.strip() for v in value.split(",") if v)

    if isinstance(value, Sequence):
        return value

    raise ValueError("Expected a comma-separated string")


def coerce_to_tuple(value: Sequence) -> tuple[str]:
    return tuple(v for v in value)
