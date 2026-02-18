"""Anthropic Messages API request types.

This module provides Pydantic models for constructing Anthropic Messages API
requests through Sequrity's Control API.
"""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Content Block Types for Messages
# =============================================================================


class TextBlockParam(BaseModel):
    """Text content block."""

    text: str = Field(..., description="The text content.")
    type: Literal["text"] = Field(default="text", description="The type of the content part.")
    cache_control: dict[str, Any] | None = Field(
        default=None, description="Create a cache control breakpoint at this content block."
    )
    citations: list[dict[str, Any]] | None = Field(default=None, description="Citations supporting the text block.")

    model_config = ConfigDict(extra="forbid")


class Base64ImageSourceParam(BaseModel):
    """Base64-encoded image source."""

    type: Literal["base64"] = Field(default="base64", description="The type of image source.")
    media_type: Literal["image/jpeg", "image/png", "image/gif", "image/webp"] = Field(
        ..., description="The media type of the image."
    )
    data: str = Field(..., description="The base64-encoded image data.")

    model_config = ConfigDict(extra="forbid")


class URLImageSourceParam(BaseModel):
    """URL image source."""

    type: Literal["url"] = Field(default="url", description="The type of image source.")
    url: str = Field(..., description="The URL of the image.")

    model_config = ConfigDict(extra="forbid")


ImageSource = Annotated[
    Base64ImageSourceParam | URLImageSourceParam,
    Field(discriminator="type"),
]


class ImageBlockParam(BaseModel):
    """Image content block."""

    source: ImageSource = Field(..., description="The source of the image.")
    type: Literal["image"] = Field(default="image", description="The type of the content part.")
    cache_control: dict[str, Any] | None = Field(
        default=None, description="Create a cache control breakpoint at this content block."
    )

    model_config = ConfigDict(extra="forbid")


class Base64DocumentSourceParam(BaseModel):
    """Base64-encoded document source."""

    type: Literal["base64"] = Field(default="base64", description="The type of document source.")
    media_type: Literal["application/pdf"] = Field(..., description="The media type of the document.")
    data: str = Field(..., description="The base64-encoded document data.")

    model_config = ConfigDict(extra="forbid")


class DocumentBlockParam(BaseModel):
    """Document content block (PDF)."""

    source: Base64DocumentSourceParam = Field(..., description="The source of the document.")
    type: Literal["document"] = Field(default="document", description="The type of the content part.")
    cache_control: dict[str, Any] | None = Field(
        default=None, description="Create a cache control breakpoint at this content block."
    )

    model_config = ConfigDict(extra="forbid")


class ToolUseBlockParam(BaseModel):
    """Tool use content block in assistant messages."""

    id: str = Field(..., description="A unique identifier for this particular tool use block.")
    input: dict[str, Any] = Field(..., description="An object containing the input being passed to the tool.")
    name: str = Field(..., description="The name of the tool being used.")
    type: Literal["tool_use"] = Field(default="tool_use", description="The type of the content part.")
    cache_control: dict[str, Any] | None = Field(
        default=None, description="Create a cache control breakpoint at this content block."
    )

    model_config = ConfigDict(extra="forbid")


class ToolResultBlockParam(BaseModel):
    """Tool result content block in user messages."""

    tool_use_id: str = Field(
        ...,
        description="The id of the tool use request this is a result for. Must match an id from a previous tool_use block.",
    )
    type: Literal["tool_result"] = Field(default="tool_result", description="The type of the content part.")
    content: str | list[TextBlockParam | ImageBlockParam | DocumentBlockParam] | None = Field(
        default=None, description="The result of the tool call."
    )
    is_error: bool | None = Field(default=None, description="Set to true if the tool execution resulted in an error.")
    cache_control: dict[str, Any] | None = Field(
        default=None, description="Create a cache control breakpoint at this content block."
    )

    model_config = ConfigDict(extra="forbid")


class ThinkingBlockParam(BaseModel):
    """Thinking content block for extended thinking."""

    text: str = Field(..., description="The thinking content.")
    type: Literal["thinking"] = Field(default="thinking", description="The type of the content part.")
    cache_control: dict[str, Any] | None = Field(
        default=None, description="Create a cache control breakpoint at this content block."
    )

    model_config = ConfigDict(extra="forbid")


MessageContentBlockParam = Annotated[
    TextBlockParam
    | ImageBlockParam
    | DocumentBlockParam
    | ToolUseBlockParam
    | ToolResultBlockParam
    | ThinkingBlockParam,
    Field(discriminator="type"),
]


# =============================================================================
# Message Types
# =============================================================================


class MessageParam(BaseModel):
    """A message in the conversation."""

    role: Literal["user", "assistant"] = Field(
        ..., description="The role of the message author: 'user' or 'assistant'."
    )
    content: str | list[MessageContentBlockParam] = Field(
        ...,
        description="The contents of the message. Can be a string or an array of content blocks.",
    )

    model_config = ConfigDict(extra="forbid")


# =============================================================================
# Tool Definition Types
# =============================================================================


class ToolInputSchema(BaseModel):
    """JSON Schema for tool input parameters."""

    type: Literal["object"] = Field(default="object", description="The type of the input schema. Always 'object'.")
    properties: dict[str, Any] | None = Field(
        default=None, description="The properties of the input schema as a JSON Schema object."
    )
    required: list[str] | None = Field(default=None, description="The required properties of the input schema.")

    model_config = ConfigDict(extra="allow")


class ToolParam(BaseModel):
    """Tool definition for the Anthropic Messages API."""

    name: str = Field(..., description="Name of the tool. This is how the tool will be called by the model.")
    input_schema: ToolInputSchema | dict[str, Any] = Field(
        ...,
        description="JSON schema for this tool's input. Defines the shape of the input that the model will produce.",
    )
    description: str | None = Field(
        default=None,
        description="Description of what this tool does. Tool descriptions should be as detailed as possible.",
    )
    cache_control: dict[str, Any] | None = Field(
        default=None, description="Create a cache control breakpoint at this content block."
    )
    strict: bool | None = Field(
        default=None, description="When true, guarantees schema validation on tool names and inputs."
    )
    type: Literal["custom"] | None = Field(default=None, description="The type of the tool.")

    model_config = ConfigDict(extra="forbid")


ToolUnionParam = ToolParam | dict[str, Any]


# =============================================================================
# Tool Choice Types
# =============================================================================


class ToolChoiceAutoParam(BaseModel):
    """Auto tool choice — model decides whether to use tools."""

    type: Literal["auto"] = Field(default="auto", description="The model will automatically decide whether to use tools.")
    disable_parallel_tool_use: bool | None = Field(
        default=None,
        description="Whether to disable parallel tool use. If true, the model will output at most one tool use.",
    )

    model_config = ConfigDict(extra="forbid")


class ToolChoiceAnyParam(BaseModel):
    """Any tool choice — model must use at least one tool."""

    type: Literal["any"] = Field(default="any", description="The model will use any available tools.")
    disable_parallel_tool_use: bool | None = Field(
        default=None,
        description="Whether to disable parallel tool use. If true, the model will output exactly one tool use.",
    )

    model_config = ConfigDict(extra="forbid")


class ToolChoiceToolParam(BaseModel):
    """Specific tool choice — model must use the named tool."""

    type: Literal["tool"] = Field(default="tool", description="The model will use the specified tool.")
    name: str = Field(..., description="The name of the tool to use.")
    disable_parallel_tool_use: bool | None = Field(
        default=None,
        description="Whether to disable parallel tool use. If true, the model will output exactly one tool use.",
    )

    model_config = ConfigDict(extra="forbid")


class ToolChoiceNoneParam(BaseModel):
    """None tool choice — model will not use tools."""

    type: Literal["none"] = Field(default="none", description="The model will not use any tools.")

    model_config = ConfigDict(extra="forbid")


ToolChoiceParam = Annotated[
    ToolChoiceAutoParam | ToolChoiceAnyParam | ToolChoiceToolParam | ToolChoiceNoneParam,
    Field(discriminator="type"),
]


# =============================================================================
# Metadata Types
# =============================================================================


class MetadataParam(BaseModel):
    """Request metadata."""

    user_id: str | None = Field(
        default=None,
        description="An external identifier for the user associated with the request. Should be a uuid, hash, or other opaque identifier.",
    )

    model_config = ConfigDict(extra="forbid")


# =============================================================================
# Output Config Types
# =============================================================================


class JSONOutputFormatParam(BaseModel):
    """JSON output format with schema."""

    type: Literal["json_schema"] = Field(default="json_schema", description="The type of the output format.")
    schema_: dict[str, Any] = Field(..., alias="schema", description="The JSON schema of the format.")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class OutputConfigParam(BaseModel):
    """Output configuration for structured responses."""

    format: JSONOutputFormatParam | None = Field(
        default=None, description="A schema to specify Claude's output format in responses."
    )

    model_config = ConfigDict(extra="forbid")


# =============================================================================
# Thinking Config Types
# =============================================================================


class ThinkingConfigEnabledParam(BaseModel):
    """Extended thinking enabled configuration."""

    type: Literal["enabled"] = Field(default="enabled", description="Thinking is enabled.")
    budget_tokens: int = Field(..., description="The maximum number of tokens to use for thinking. Minimum is 1024.")

    model_config = ConfigDict(extra="forbid")


class ThinkingConfigDisabledParam(BaseModel):
    """Extended thinking disabled configuration."""

    type: Literal["disabled"] = Field(default="disabled", description="Thinking is disabled.")

    model_config = ConfigDict(extra="forbid")


ThinkingConfigParam = Annotated[
    ThinkingConfigEnabledParam | ThinkingConfigDisabledParam,
    Field(discriminator="type"),
]


# =============================================================================
# Main Request Class
# =============================================================================


class AnthropicMessageRequest(BaseModel):
    """Anthropic Messages API request.

    This is a Pydantic model representation of the Anthropic Messages API request,
    used for sending messages through Sequrity's Control API with the Messages format.
    """

    # Required fields
    max_tokens: int = Field(
        ...,
        description="The maximum number of tokens to generate before stopping.",
    )
    messages: list[MessageParam] = Field(
        ...,
        description="Input messages with alternating user and assistant conversational turns.",
    )
    model: str = Field(
        ...,
        description="The model that will complete your prompt (e.g., 'claude-3-opus', 'claude-4-sonnet').",
    )

    # Optional fields
    metadata: MetadataParam | None = Field(default=None, description="An object describing metadata about the request.")
    output_config: OutputConfigParam | None = Field(
        default=None, description="Configuration options for the model's output, such as the output format."
    )
    service_tier: Literal["auto", "standard_only"] | None = Field(
        default=None,
        description="Determines whether to use priority capacity or standard capacity for this request.",
    )
    stop_sequences: list[str] | None = Field(
        default=None,
        description="Custom text sequences that will cause the model to stop generating.",
    )
    stream: bool | None = Field(
        default=None, description="Whether to incrementally stream the response using server-sent events."
    )
    system: str | list[TextBlockParam] | None = Field(
        default=None,
        description="System prompt providing context and instructions to the model.",
    )
    temperature: float | None = Field(
        default=None,
        description="Amount of randomness injected into the response. Ranges from 0.0 to 1.0.",
    )
    thinking: ThinkingConfigParam | None = Field(
        default=None,
        description="Configuration for enabling extended thinking. When enabled, responses include thinking content blocks.",
    )
    tool_choice: ToolChoiceParam | None = Field(
        default=None, description="How the model should use the provided tools."
    )
    tools: list[ToolUnionParam] | None = Field(
        default=None,
        description="Definitions of tools that the model may use.",
    )
    top_k: int | None = Field(
        default=None,
        description="Only sample from the top K options for each subsequent token.",
    )
    top_p: float | None = Field(
        default=None,
        description="Use nucleus sampling with the specified probability threshold.",
    )
    timeout: float | None = Field(
        default=None,
        description="The maximum amount of time, in seconds, that the request should take.",
    )

    model_config = ConfigDict(extra="ignore")
