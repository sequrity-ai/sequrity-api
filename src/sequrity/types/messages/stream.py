"""
Pydantic models for Anthropic RawMessageStreamEvent types.

See: anthropic.types.RawMessageStreamEvent

Anthropic uses a discriminated union of 6 event types for streaming,
each carrying different data.
"""

from typing import Annotated, Any, Literal, Union

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Delta Types (for content_block_delta events)
# =============================================================================


class TextDelta(BaseModel):
    type: Literal["text_delta"] = "text_delta"
    text: str


class InputJSONDelta(BaseModel):
    type: Literal["input_json_delta"] = "input_json_delta"
    partial_json: str


class ThinkingDelta(BaseModel):
    type: Literal["thinking_delta"] = "thinking_delta"
    thinking: str


class SignatureDelta(BaseModel):
    type: Literal["signature_delta"] = "signature_delta"
    signature: str


class CitationsDelta(BaseModel):
    type: Literal["citations_delta"] = "citations_delta"
    citation: dict[str, Any]

    model_config = ConfigDict(extra="allow")


AnthropicContentDelta: TypeAlias = Annotated[
    Union[TextDelta, InputJSONDelta, ThinkingDelta, SignatureDelta, CitationsDelta],
    Field(discriminator="type"),
]


# =============================================================================
# Content Block Start Types (for content_block_start events)
# =============================================================================


class TextBlockStart(BaseModel):
    """TextBlock as it appears in content_block_start (empty text)."""

    type: Literal["text"] = "text"
    text: str = ""
    citations: list[dict[str, Any]] | None = None


class ThinkingBlockStart(BaseModel):
    """ThinkingBlock as it appears in content_block_start."""

    type: Literal["thinking"] = "thinking"
    thinking: str = ""
    signature: str = ""


class RedactedThinkingBlockStart(BaseModel):
    """RedactedThinkingBlock as it appears in content_block_start."""

    type: Literal["redacted_thinking"] = "redacted_thinking"


class ToolUseBlockStart(BaseModel):
    """ToolUseBlock as it appears in content_block_start (input is always {})."""

    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict[str, Any] = Field(default_factory=dict)


class ServerToolUseBlockStart(BaseModel):
    """ServerToolUseBlock as it appears in content_block_start."""

    type: Literal["server_tool_use"] = "server_tool_use"
    id: str
    name: str

    model_config = ConfigDict(extra="allow")


AnthropicContentBlockStart: TypeAlias = Annotated[
    Union[TextBlockStart, ThinkingBlockStart, RedactedThinkingBlockStart, ToolUseBlockStart, ServerToolUseBlockStart],
    Field(discriminator="type"),
]


# =============================================================================
# Message Delta Types
# =============================================================================


class MessageDeltaBody(BaseModel):
    stop_reason: Literal["end_turn", "max_tokens", "stop_sequence", "tool_use", "pause_turn", "refusal"] | None = None
    stop_sequence: str | None = None


class MessageDeltaUsage(BaseModel):
    output_tokens: int
    input_tokens: int | None = None
    cache_creation_input_tokens: int | None = None
    cache_read_input_tokens: int | None = None

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# The 6 Event Types
# =============================================================================


class RawMessageStartEvent(BaseModel):
    """Carries the initial Message object with metadata and usage."""

    type: Literal["message_start"] = "message_start"
    message: dict[str, Any] = Field(description="Full Message object as dict (id, model, role, content, usage, etc.).")

    model_config = ConfigDict(extra="ignore")


class RawContentBlockStartEvent(BaseModel):
    """A new content block begins."""

    type: Literal["content_block_start"] = "content_block_start"
    index: int
    content_block: AnthropicContentBlockStart

    model_config = ConfigDict(extra="ignore")


class RawContentBlockDeltaEvent(BaseModel):
    """Incremental content within a block."""

    type: Literal["content_block_delta"] = "content_block_delta"
    index: int
    delta: AnthropicContentDelta

    model_config = ConfigDict(extra="ignore")


class RawContentBlockStopEvent(BaseModel):
    """A content block has ended."""

    type: Literal["content_block_stop"] = "content_block_stop"
    index: int

    model_config = ConfigDict(extra="ignore")


class RawMessageDeltaEvent(BaseModel):
    """End-of-stream metadata: stop reason and usage update."""

    type: Literal["message_delta"] = "message_delta"
    delta: MessageDeltaBody
    usage: MessageDeltaUsage

    model_config = ConfigDict(extra="ignore")


class RawMessageStopEvent(BaseModel):
    """Terminal event: stream is complete."""

    type: Literal["message_stop"] = "message_stop"

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Union Type
# =============================================================================

AnthropicStreamEvent: TypeAlias = Annotated[
    Union[
        RawMessageStartEvent,
        RawContentBlockStartEvent,
        RawContentBlockDeltaEvent,
        RawContentBlockStopEvent,
        RawMessageDeltaEvent,
        RawMessageStopEvent,
    ],
    Field(discriminator="type"),
]
