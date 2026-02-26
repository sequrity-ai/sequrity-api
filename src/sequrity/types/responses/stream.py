"""
Pydantic models for OpenAI Responses API streaming events.

See: openai.types.responses.ResponseStreamEvent

Events are grouped into:
- Lifecycle: response created / in_progress / completed / failed / incomplete
- Structure: output_item added/done, content_part added/done
- Content:   text delta/done, function_call_arguments delta/done
- Reasoning: reasoning_summary_text delta/done, reasoning_summary_part added/done
"""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Lifecycle Events
# =============================================================================


class ResponseCreatedEvent(BaseModel):
    """Emitted once when the response is first created."""

    type: Literal["response.created"] = "response.created"
    response: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseInProgressEvent(BaseModel):
    """Emitted when the response transitions to in_progress."""

    type: Literal["response.in_progress"] = "response.in_progress"
    response: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseCompletedEvent(BaseModel):
    """Emitted when the response completes successfully."""

    type: Literal["response.completed"] = "response.completed"
    response: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseFailedEvent(BaseModel):
    """Emitted when the response fails."""

    type: Literal["response.failed"] = "response.failed"
    response: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseIncompleteEvent(BaseModel):
    """Emitted when the response is incomplete (e.g. max_tokens)."""

    type: Literal["response.incomplete"] = "response.incomplete"
    response: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Output Item Events
# =============================================================================


class ResponseOutputItemAddedEvent(BaseModel):
    """Emitted when a new output item (message, reasoning, function_call) starts."""

    type: Literal["response.output_item.added"] = "response.output_item.added"
    output_index: int
    item: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseOutputItemDoneEvent(BaseModel):
    """Emitted when an output item is fully completed."""

    type: Literal["response.output_item.done"] = "response.output_item.done"
    output_index: int
    item: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Content Part Events (within message output items)
# =============================================================================


class ResponseContentPartAddedEvent(BaseModel):
    """Emitted when a new content part starts within a message."""

    type: Literal["response.content_part.added"] = "response.content_part.added"
    item_id: str
    output_index: int
    content_index: int
    part: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseContentPartDoneEvent(BaseModel):
    """Emitted when a content part within a message is completed."""

    type: Literal["response.content_part.done"] = "response.content_part.done"
    item_id: str
    output_index: int
    content_index: int
    part: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Text Content Events
# =============================================================================


class ResponseTextDeltaEvent(BaseModel):
    """Incremental text content within an output_text content part."""

    type: Literal["response.output_text.delta"] = "response.output_text.delta"
    item_id: str
    output_index: int
    content_index: int
    delta: str
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseTextDoneEvent(BaseModel):
    """Emitted when an output_text content part is finalized."""

    type: Literal["response.output_text.done"] = "response.output_text.done"
    item_id: str
    output_index: int
    content_index: int
    text: str
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Function Call Events
# =============================================================================


class ResponseFunctionCallArgumentsDeltaEvent(BaseModel):
    """Incremental function call arguments."""

    type: Literal["response.function_call_arguments.delta"] = "response.function_call_arguments.delta"
    item_id: str
    output_index: int
    delta: str
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseFunctionCallArgumentsDoneEvent(BaseModel):
    """Emitted when function call arguments are finalized."""

    type: Literal["response.function_call_arguments.done"] = "response.function_call_arguments.done"
    item_id: str
    output_index: int
    name: str
    arguments: str
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Reasoning Summary Events
# =============================================================================


class ResponseReasoningSummaryPartAddedEvent(BaseModel):
    """Emitted when a new reasoning summary part starts."""

    type: Literal["response.reasoning_summary_part.added"] = "response.reasoning_summary_part.added"
    item_id: str
    output_index: int
    summary_index: int
    part: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseReasoningSummaryPartDoneEvent(BaseModel):
    """Emitted when a reasoning summary part is completed."""

    type: Literal["response.reasoning_summary_part.done"] = "response.reasoning_summary_part.done"
    item_id: str
    output_index: int
    summary_index: int
    part: dict[str, Any]
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseReasoningSummaryTextDeltaEvent(BaseModel):
    """Incremental reasoning summary text."""

    type: Literal["response.reasoning_summary_text.delta"] = "response.reasoning_summary_text.delta"
    item_id: str
    output_index: int
    summary_index: int
    delta: str
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


class ResponseReasoningSummaryTextDoneEvent(BaseModel):
    """Emitted when reasoning summary text is finalized."""

    type: Literal["response.reasoning_summary_text.done"] = "response.reasoning_summary_text.done"
    item_id: str
    output_index: int
    summary_index: int
    text: str
    sequence_number: int

    model_config = ConfigDict(extra="ignore")


# =============================================================================
# Union Type
# =============================================================================

type OpenAiResponseStreamEvent = Annotated[
    ResponseCreatedEvent
    | ResponseInProgressEvent
    | ResponseCompletedEvent
    | ResponseFailedEvent
    | ResponseIncompleteEvent
    | ResponseOutputItemAddedEvent
    | ResponseOutputItemDoneEvent
    | ResponseContentPartAddedEvent
    | ResponseContentPartDoneEvent
    | ResponseTextDeltaEvent
    | ResponseTextDoneEvent
    | ResponseFunctionCallArgumentsDeltaEvent
    | ResponseFunctionCallArgumentsDoneEvent
    | ResponseReasoningSummaryPartAddedEvent
    | ResponseReasoningSummaryPartDoneEvent
    | ResponseReasoningSummaryTextDeltaEvent
    | ResponseReasoningSummaryTextDoneEvent,
    Field(discriminator="type"),
]
