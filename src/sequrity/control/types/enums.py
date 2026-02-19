"""Enumerations specific to Sequrity Control."""

from enum import StrEnum


class EndpointType(StrEnum):
    """Endpoint type determining the security processing pipeline."""

    CHAT = "chat"
    CODE = "code"
    AGENT = "agent"
    LANGGRAPH = "lang-graph"
