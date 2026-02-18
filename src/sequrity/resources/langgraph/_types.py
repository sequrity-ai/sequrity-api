"""Internal types used by the LangGraph resource."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ...types.chat_completion.request import ChatCompletionRequest
from ...types.chat_completion.response import ChatCompletionResponse
from ...types.dual_llm_response import (
    ErrorInfo,
    MetaData,
    ResponseContentJsonSchema,
    ValueWithMeta,
)
from ...types.messages.request import AnthropicMessageRequest

# Re-export for backwards compatibility
__all__ = [
    "ErrorInfo",
    "MetaData",
    "ResponseContentJsonSchema",
    "ValueWithMeta",
    "LangGraphRequestMixin",
    "LangGraphChatCompletionRequest",
    "LangGraphChatCompletionResponse",
    "LangGraphMessagesRequest",
]


class LangGraphRequestMixin(BaseModel):
    """Mixin adding LangGraph-specific fields to any provider request."""

    user_provided_program: str | None = Field(
        default=None,
        description="The user-provided Python program to execute.",
    )
    context_vars: dict[str, ValueWithMeta] | None = Field(
        default=None,
        description="Predefined variables with meta for the interpreter.",
    )


class LangGraphChatCompletionRequest(ChatCompletionRequest, LangGraphRequestMixin):
    """Extended chat completion request for LangGraph execution (OpenAI-compatible providers)."""

    pass


class LangGraphMessagesRequest(AnthropicMessageRequest, LangGraphRequestMixin):
    """Extended Anthropic Messages request for LangGraph execution."""

    pass


class LangGraphChatCompletionResponse(ChatCompletionResponse):
    """Chat completion response from LangGraph execution."""

    pass
