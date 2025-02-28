from copy import deepcopy
from typing import Any


class StructuredError(Exception):
    """
    The base exception class for all structured errors

    Structured errors contain fields/properties that allows for more flexible
    handling and logging of errors.

    :param message: The error message
    :param kwargs: Additional attributes to include in the error

    Example:

    .. code-block:: python

        >>> from service_kit.errors import StructuredError
        >>> err = StructuredError("my message", attr1="a1", attr2="a2")
        >>> str(err)
        'my message'
        >>> err.message
        'my message'
        >>> err.attr1
        'a1'
        >>> err.attr2
        'a2'
        >>> err.structured_error
        {'attr1': 'a1', 'attr2': 'a2', 'message': 'my message'}

    """

    def __init__(self, message, /, **kwargs):
        super().__init__(message)
        self._attributes = kwargs
        self._attributes["message"] = message

    def __getattr__(self, name):
        try:
            return self._attributes[name]
        except KeyError:
            raise AttributeError(name)

    @property
    def structured_error(self) -> dict[str, Any]:
        """A structured representation of the error"""
        return deepcopy(self._attributes)
