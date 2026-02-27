"""
Pydantic models for OpenAI ChatCompletionChunk streaming types.

See: openai.types.chat.ChatCompletionChunk
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Nested Types
# =============================================================================


class ChunkChoiceDeltaFunctionCall(BaseModel):
    """Function call delta within a tool call."""

    name: str | None = None
    arguments: str | None = None


class ChunkChoiceDeltaToolCall(BaseModel):
    """A single tool call delta within a streaming choice."""

    index: int
    id: str | None = None
    type: Literal["function"] | None = None
    function: ChunkChoiceDeltaFunctionCall | None = None


class ChunkChoiceDelta(BaseModel):
    """Delta object within a streaming choice."""

    role: Literal["assistant"] | None = None
    content: str | None = None
    refusal: str | None = None
    tool_calls: list[ChunkChoiceDeltaToolCall] | None = None
    reasoning_content: str | None = Field(
        default=None,
        description="Reasoning content (non-standard extension used by some providers via OpenAI-compatible API).",
    )

    model_config = ConfigDict(extra="ignore")


class ChunkChoiceLogprobs(BaseModel):
    """Logprob information for a streaming choice."""

    content: list[dict] | None = None
    refusal: list[dict] | None = None

    model_config = ConfigDict(extra="allow")


class ChunkChoice(BaseModel):
    """A single choice in a streaming chunk."""

    index: int
    delta: ChunkChoiceDelta
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter", "function_call"] | None = None
    logprobs: ChunkChoiceLogprobs | None = None

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Usage (optional, on final chunk when stream_options.include_usage=true)
# =============================================================================


class ChunkCompletionTokensDetails(BaseModel):
    accepted_prediction_tokens: int | None = None
    audio_tokens: int | None = None
    reasoning_tokens: int | None = None
    rejected_prediction_tokens: int | None = None

    model_config = ConfigDict(extra="ignore")


class ChunkPromptTokensDetails(BaseModel):
    audio_tokens: int | None = None
    cached_tokens: int | None = None

    model_config = ConfigDict(extra="ignore")


class ChunkCompletionUsage(BaseModel):
    """Usage stats on the final chunk."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    completion_tokens_details: ChunkCompletionTokensDetails | None = None
    prompt_tokens_details: ChunkPromptTokensDetails | None = None

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Root Chunk Type
# =============================================================================


class ChatCompletionChunk(BaseModel):
    """OpenAI ChatCompletionChunk for streaming responses."""

    id: str
    choices: list[ChunkChoice]
    created: int
    model: str
    object: Literal["chat.completion.chunk"]
    service_tier: Literal["auto", "default", "flex", "scale", "priority"] | None = None
    system_fingerprint: str | None = None
    usage: ChunkCompletionUsage | None = None

    model_config = ConfigDict(extra="ignore")
