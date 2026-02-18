"""Sequrity universal type definitions.

Provider-agnostic types shared across all Sequrity products.

For Control-specific types (headers, dual-LLM response, etc.), import from
``sequrity.control``::

    from sequrity.control import FeaturesHeader, SecurityPolicyHeader
"""

from .enums import LlmServiceProvider, RestApiType

__all__ = [
    "RestApiType",
    "LlmServiceProvider",
]
