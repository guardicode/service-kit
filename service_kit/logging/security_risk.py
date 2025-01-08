from enum import StrEnum


class SecurityRisk(StrEnum):
    """
    Used in log messages with security-related content to express the risk/severity of the event
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
