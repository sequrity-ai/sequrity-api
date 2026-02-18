"""Sequrity API Python client.

This package provides a Python client for interacting with the Sequrity API,
enabling secure LLM interactions with policy enforcement.

Product-specific types (headers, configs) are imported from their respective
product packages::

    from sequrity.control import FeaturesHeader, SecurityPolicyHeader, ControlConfig
"""

from ._client import AsyncSequrityClient, SequrityClient
from ._exceptions import (
    SequrityAPIError,
    SequrityConnectionError,
    SequrityError,
    SequrityValidationError,
)
from .types.enums import LlmServiceProvider, RestApiType

# Universal provider request/response types
from .types.chat_completion.request import ChatCompletionRequest
from .types.chat_completion.response import ChatCompletionResponse
from .types.messages.request import AnthropicMessageRequest
from .types.messages.response import AnthropicMessageResponse

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

__all__ = [
    # Clients
    "SequrityClient",
    "AsyncSequrityClient",
    # Exceptions
    "SequrityError",
    "SequrityAPIError",
    "SequrityValidationError",
    "SequrityConnectionError",
    # Enums (universal)
    "RestApiType",
    "LlmServiceProvider",
    # Universal request/response types
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "AnthropicMessageRequest",
    "AnthropicMessageResponse",
    # Version
    "__version__",
]
