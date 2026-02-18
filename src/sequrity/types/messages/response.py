"""Anthropic Messages API response types.

This module provides Pydantic models for parsing Anthropic Messages API
responses from Sequrity's Control API.
"""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Content Block Types for Response
# =============================================================================


class TextCitation(BaseModel):
    """Citation supporting a text block."""

    type: str = Field(..., description="The type of citation (e.g., page_location, char_location).")

    model_config = ConfigDict(extra="allow")


class TextBlock(BaseModel):
    """Text content block in the response."""

    type: Literal["text"] = Field(..., description="The type of the content block.")
    text: str = Field(..., description="The text content.")
    citations: list[TextCitation] | None = Field(
        default=None,
        description="Citations supporting the text block.",
    )

    model_config = ConfigDict(extra="forbid")


class ThinkingBlock(BaseModel):
    """Thinking content block showing the model's reasoning process."""

    type: Literal["thinking"] = Field(..., description="The type of the content block.")
    text: str = Field(..., description="The thinking content.")

    model_config = ConfigDict(extra="forbid")


class RedactedThinkingBlock(BaseModel):
    """Redacted thinking content block."""

    type: Literal["redacted_thinking"] = Field(..., description="The type of the content block.")

    model_config = ConfigDict(extra="allow")


class ToolUseBlock(BaseModel):
    """Tool use content block — the model wants to call a tool."""

    type: Literal["tool_use"] = Field(..., description="The type of the content block.")
    id: str = Field(..., description="A unique identifier for this particular tool use block.")
    name: str = Field(..., description="The name of the tool being used.")
    input: dict[str, Any] = Field(..., description="An object containing the input being passed to the tool.")

    model_config = ConfigDict(extra="forbid")


class ServerToolUseBlock(BaseModel):
    """Server tool use content block (e.g., bash, web search)."""

    type: Literal["server_tool_use"] = Field(..., description="The type of the content block.")
    id: str = Field(..., description="A unique identifier for this server tool use block.")
    name: str = Field(..., description="The name of the server tool being used.")

    model_config = ConfigDict(extra="allow")


class WebSearchToolResultBlock(BaseModel):
    """Web search tool result content block."""

    type: Literal["web_search_tool_result"] = Field(..., description="The type of the content block.")

    model_config = ConfigDict(extra="allow")


ContentBlock = Annotated[
    TextBlock | ThinkingBlock | RedactedThinkingBlock | ToolUseBlock | ServerToolUseBlock | WebSearchToolResultBlock,
    Field(discriminator="type"),
]


# =============================================================================
# Usage Statistics
# =============================================================================


class CacheCreation(BaseModel):
    """Breakdown of cached tokens by TTL."""

    model_config = ConfigDict(extra="allow")


class ServerToolUsage(BaseModel):
    """The number of server tool requests."""

    model_config = ConfigDict(extra="allow")


class Usage(BaseModel):
    """Token usage statistics for the request."""

    input_tokens: int = Field(..., description="The number of input tokens which were used.")
    output_tokens: int = Field(..., description="The number of output tokens which were used.")
    cache_creation_input_tokens: int | None = Field(
        default=None, description="The number of input tokens used to create the cache entry."
    )
    cache_read_input_tokens: int | None = Field(
        default=None, description="The number of input tokens read from the cache."
    )
    cache_creation: CacheCreation | None = Field(default=None, description="Breakdown of cached tokens by TTL.")
    server_tool_use: ServerToolUsage | None = Field(default=None, description="The number of server tool requests.")
    service_tier: Literal["standard", "priority", "batch"] | None = Field(
        default=None, description="If the request used the priority, standard, or batch tier."
    )

    model_config = ConfigDict(extra="forbid")


# =============================================================================
# Main Response Class
# =============================================================================


class AnthropicMessageResponse(BaseModel):
    """Anthropic Messages API response.

    This is a Pydantic model representation of the Anthropic Messages API response,
    returned by Sequrity's Control API when using the Messages format.
    """

    id: str = Field(..., description="Unique object identifier.")
    type: Literal["message"] = Field(..., description="Object type. Always 'message'.")
    role: Literal["assistant"] = Field(
        ..., description="Conversational role of the generated message. Always 'assistant'."
    )
    content: list[ContentBlock] = Field(
        ...,
        description="Content generated by the model as an array of content blocks.",
    )
    model: str = Field(
        ...,
        description="The model that handled the request.",
    )
    stop_reason: Literal["end_turn", "max_tokens", "stop_sequence", "tool_use", "pause_turn", "refusal"] | None = Field(
        default=None,
        description="The reason the model stopped generating.",
    )
    stop_sequence: str | None = Field(
        default=None,
        description="Which custom stop sequence was generated, if any.",
    )
    usage: Usage = Field(
        ...,
        description="Billing and rate-limit usage statistics.",
    )
    session_id: str | None = Field(
        default=None, description="The Sequrity session ID associated with this response."
    )

    model_config = ConfigDict(extra="ignore")
