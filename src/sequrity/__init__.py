"""Sequrity API Python client.

This package provides a Python client for interacting with the Sequrity API,
enabling secure LLM interactions with policy enforcement.
"""

from ._client import AsyncSequrityClient, SequrityClient
from ._exceptions import (
    SequrityAPIError,
    SequrityConnectionError,
    SequrityError,
    SequrityValidationError,
)
from .types.enums import EndpointType, LlmServiceProvider, RestApiType
from .types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader

# Type re-exports for users who need request/response types
from .types.chat_completion.request import ChatCompletionRequest
from .types.chat_completion.response import ChatCompletionResponse
from .types.messages.request import AnthropicMessageRequest
from .types.messages.response import AnthropicMessageResponse
from .types.policy_gen import PolicyGenRequest, PolicyGenResponse

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
    # Enums
    "EndpointType",
    "RestApiType",
    "LlmServiceProvider",
    # Headers
    "FeaturesHeader",
    "SecurityPolicyHeader",
    "FineGrainedConfigHeader",
    # Request/Response types
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "AnthropicMessageRequest",
    "AnthropicMessageResponse",
    "PolicyGenRequest",
    "PolicyGenResponse",
    # Version
    "__version__",
]
