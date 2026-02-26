"""Pydantic models for OpenAI Responses API request types."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Input Content Types
# =============================================================================


class InputTextParam(BaseModel):
    text: str = Field(..., description="The text content.")
    type: Literal["input_text"] = Field(
        ..., description="The type of the input content."
    )


class InputImageParam(BaseModel):
    """An image input. Supports both URL and file_id references."""

    type: Literal["input_image"] = Field(
        ..., description="The type of the input content."
    )
    detail: Literal["auto", "low", "high"] | None = Field(
        default=None, description="The detail level of the image."
    )
    file_id: str | None = Field(
        default=None, description="The ID of the uploaded file."
    )
    image_url: str | None = Field(
        default=None, description="The URL of the image or base64 data URL."
    )


class InputFileParam(BaseModel):
    file_id: str = Field(..., description="The ID of the uploaded file.")
    type: Literal["input_file"] = Field(
        ..., description="The type of the input content."
    )


class InputAudioParam(BaseModel):
    audio: str = Field(..., description="Base64-encoded audio data.")
    type: Literal["input_audio"] = Field(
        ..., description="The type of the input content."
    )


InputContentParam = Annotated[
    InputTextParam | InputImageParam | InputFileParam | InputAudioParam,
    Field(discriminator="type"),
]

# =============================================================================
# Message Types
# =============================================================================


class InputMessageParam(BaseModel):
    role: Literal["user", "system", "developer"] = Field(
        ...,
        description="The role of the message. One of 'user', 'system', or 'developer'.",
    )
    content: str | list[InputContentParam] = Field(
        ...,
        description="The content of the message. Can be a string or list of content items.",
    )


# =============================================================================
# Message (type="message") - full message with status, distinct from InputMessageParam
# =============================================================================


class MessageParam(BaseModel):
    """A message input to the model with a role indicating instruction following hierarchy."""

    content: str | list[InputContentParam] = Field(
        ...,
        description="A list of one or many input items to the model, containing different content types.",
    )
    role: Literal["user", "system", "developer"] = Field(
        ...,
        description="The role of the message input. One of 'user', 'system', or 'developer'.",
    )
    type: Literal["message"] = Field(
        ..., description="The type of the message input. Always 'message'."
    )
    status: Literal["in_progress", "completed", "incomplete"] | None = Field(
        default=None, description="The status of the item."
    )


# =============================================================================
# Output Content Types (for ResponseOutputMessageParam)
# =============================================================================


class OutputTextParam(BaseModel):
    """A text output from the model."""

    text: str = Field(..., description="The text output from the model.")
    type: Literal["output_text"] = Field(
        ..., description="The type of the output text. Always 'output_text'."
    )
    annotations: list[dict[str, Any]] | None = Field(
        default=None, description="Annotations for the text, such as citations."
    )


class OutputRefusalParam(BaseModel):
    """A refusal from the model."""

    refusal: str = Field(..., description="The refusal explanation from the model.")
    type: Literal["refusal"] = Field(
        ..., description="The type of the refusal. Always 'refusal'."
    )


OutputMessageContentParam = Annotated[
    OutputTextParam | OutputRefusalParam,
    Field(discriminator="type"),
]


class ResponseOutputMessageParam(BaseModel):
    """An output message from the model, used as input for multi-turn conversations."""

    id: str = Field(..., description="The unique ID of the output message.")
    content: list[OutputMessageContentParam] = Field(
        ..., description="The content of the output message."
    )
    role: Literal["assistant"] = Field(
        ..., description="The role of the output message. Always 'assistant'."
    )
    status: Literal["in_progress", "completed", "incomplete"] = Field(
        ..., description="The status of the message."
    )
    type: Literal["message"] = Field(
        ..., description="The type of the output message. Always 'message'."
    )


# =============================================================================
# Function Tool Call (type="function_call") - for feeding back previous tool calls
# =============================================================================


class ResponseFunctionToolCallParam(BaseModel):
    """A tool call to run a function, used as input for multi-turn conversations."""

    arguments: str = Field(
        ..., description="A JSON string of the arguments to pass to the function."
    )
    call_id: str = Field(
        ...,
        description="The unique ID of the function tool call generated by the model.",
    )
    name: str = Field(..., description="The name of the function to run.")
    type: Literal["function_call"] = Field(
        ..., description="The type of the function tool call. Always 'function_call'."
    )
    id: str | None = Field(
        default=None, description="The unique ID of the function tool call."
    )
    status: Literal["in_progress", "completed", "incomplete"] | None = Field(
        default=None, description="The status of the item."
    )


# =============================================================================
# Function Call Output (type="function_call_output") - tool result
# =============================================================================


class FunctionCallOutputParam(BaseModel):
    """The output of a function tool call."""

    call_id: str = Field(
        ...,
        description="The unique ID of the function tool call generated by the model.",
    )
    output: str = Field(..., description="Text output of the function tool call.")
    type: Literal["function_call_output"] = Field(
        ...,
        description="The type of the function tool call output. Always 'function_call_output'.",
    )
    id: str | None = Field(
        default=None, description="The unique ID of the function tool call output."
    )
    status: Literal["in_progress", "completed", "incomplete"] | None = Field(
        default=None, description="The status of the item."
    )


# =============================================================================
# Custom Tool Call (type="custom_tool_call") - for custom/grammar tools
# =============================================================================


class ResponseCustomToolCallParam(BaseModel):
    """A call to a custom tool created by the model."""

    call_id: str = Field(
        ...,
        description="An identifier used to map this custom tool call to a tool call output.",
    )
    input: str = Field(
        ..., description="The input for the custom tool call generated by the model."
    )
    name: str = Field(..., description="The name of the custom tool being called.")
    type: Literal["custom_tool_call"] = Field(
        ..., description="The type of the custom tool call. Always 'custom_tool_call'."
    )
    id: str | None = Field(
        default=None, description="The unique ID of the custom tool call."
    )


# =============================================================================
# Custom Tool Call Output (type="custom_tool_call_output") - tool result for custom tools
# =============================================================================


class ResponseCustomToolCallOutputParam(BaseModel):
    """The output of a custom tool call from your code, being sent back to the model."""

    call_id: str = Field(
        ...,
        description="The call ID, used to map this custom tool call output to a custom tool call.",
    )
    output: str = Field(
        ..., description="The output from the custom tool call generated by your code."
    )
    type: Literal["custom_tool_call_output"] = Field(
        ...,
        description="The type of the custom tool call output. Always 'custom_tool_call_output'.",
    )
    id: str | None = Field(
        default=None, description="The unique ID of the custom tool call output."
    )


# =============================================================================
# Computer Call Output (type="computer_call_output")
# =============================================================================


class ComputerCallOutputAcknowledgedSafetyCheck(BaseModel):
    id: str = Field(..., description="The safety check ID.")
    code: str | None = Field(
        default=None, description="The type of the pending safety check."
    )
    message: str | None = Field(
        default=None, description="Details about the pending safety check."
    )


class ComputerCallOutputParam(BaseModel):
    """Output from a computer tool call."""

    call_id: str = Field(..., description="The computer tool call ID.")
    output: dict[str, Any] = Field(..., description="Screenshot output.")
    type: Literal["computer_call_output"] = Field(
        ..., description="Always 'computer_call_output'."
    )
    id: str | None = Field(default=None, description="The unique ID.")
    acknowledged_safety_checks: (
        list[ComputerCallOutputAcknowledgedSafetyCheck] | None
    ) = Field(default=None, description="Acknowledged safety checks.")
    status: Literal["in_progress", "completed", "incomplete"] | None = Field(
        default=None, description="The status."
    )


# =============================================================================
# Local Shell Call types (for input)
# =============================================================================


class LocalShellCallActionParam(BaseModel):
    command: list[str] = Field(..., description="The command to run.")
    env: dict[str, str] = Field(
        default_factory=dict, description="Environment variables."
    )
    type: Literal["exec"] = Field(..., description="Always 'exec'.")
    timeout_ms: int | None = Field(
        default=None, description="Optional timeout in milliseconds."
    )
    user: str | None = Field(
        default=None, description="Optional user to run the command as."
    )
    working_directory: str | None = Field(
        default=None, description="Optional working directory."
    )


class LocalShellCallParam(BaseModel):
    """A local shell tool call."""

    id: str = Field(..., description="The unique ID.")
    action: LocalShellCallActionParam = Field(
        ..., description="The shell command to execute."
    )
    call_id: str = Field(..., description="The tool call ID from the model.")
    status: Literal["in_progress", "completed", "incomplete"] = Field(
        ..., description="The status."
    )
    type: Literal["local_shell_call"] = Field(
        ..., description="Always 'local_shell_call'."
    )


class LocalShellCallOutputParam(BaseModel):
    """Output from a local shell tool call."""

    id: str = Field(..., description="The tool call output ID.")
    output: str = Field(..., description="JSON string of output.")
    type: Literal["local_shell_call_output"] = Field(
        ..., description="Always 'local_shell_call_output'."
    )
    status: Literal["in_progress", "completed", "incomplete"] | None = Field(
        default=None, description="The status."
    )


# =============================================================================
# Shell Call types (function_shell)
# =============================================================================


class ShellCallActionParam(BaseModel):
    commands: list[str] = Field(..., description="Shell commands to run.")
    max_output_length: int | None = Field(
        default=None, description="Max output characters."
    )
    timeout_ms: int | None = Field(
        default=None, description="Max wall-clock time in ms."
    )


class ShellCallParam(BaseModel):
    """A shell command request."""

    action: ShellCallActionParam = Field(..., description="The shell action.")
    call_id: str = Field(..., description="The tool call ID.")
    type: Literal["shell_call"] = Field(..., description="Always 'shell_call'.")
    id: str | None = Field(default=None, description="The unique ID.")
    status: Literal["in_progress", "completed", "incomplete"] | None = Field(
        default=None, description="The status."
    )


class ShellCallOutputParam(BaseModel):
    """Output from a shell tool call."""

    call_id: str = Field(..., description="The shell tool call ID.")
    output: list[dict[str, Any]] = Field(..., description="Output chunks.")
    type: Literal["shell_call_output"] = Field(
        ..., description="Always 'shell_call_output'."
    )
    id: str | None = Field(default=None, description="The unique ID.")
    max_output_length: int | None = Field(
        default=None, description="Max output length."
    )


# =============================================================================
# Apply Patch Call types
# =============================================================================


class ApplyPatchCallParam(BaseModel):
    """An apply patch tool call."""

    call_id: str = Field(..., description="The tool call ID.")
    operation: dict[str, Any] = Field(
        ..., description="The file operation (create_file, delete_file, update_file)."
    )
    status: Literal["in_progress", "completed"] = Field(..., description="The status.")
    type: Literal["apply_patch_call"] = Field(
        ..., description="Always 'apply_patch_call'."
    )
    id: str | None = Field(default=None, description="The unique ID.")


class ApplyPatchCallOutputParam(BaseModel):
    """Output from an apply patch tool call."""

    call_id: str = Field(..., description="The tool call ID.")
    status: Literal["completed", "failed"] = Field(..., description="The status.")
    type: Literal["apply_patch_call_output"] = Field(
        ..., description="Always 'apply_patch_call_output'."
    )
    id: str | None = Field(default=None, description="The unique ID.")
    output: str | None = Field(default=None, description="Log text.")


# =============================================================================
# MCP types (for input)
# =============================================================================


class McpListToolsToolParam(BaseModel):
    input_schema: dict[str, Any] = Field(
        ..., description="The JSON schema describing the tool's input."
    )
    name: str = Field(..., description="The name of the tool.")
    annotations: dict[str, Any] | None = Field(
        default=None, description="Additional annotations."
    )
    description: str | None = Field(
        default=None, description="The description of the tool."
    )


class McpListToolsParam(BaseModel):
    """MCP server tools list."""

    id: str = Field(..., description="The unique ID.")
    server_label: str = Field(..., description="The MCP server label.")
    tools: list[McpListToolsToolParam] = Field(..., description="Available tools.")
    type: Literal["mcp_list_tools"] = Field(..., description="Always 'mcp_list_tools'.")
    error: str | None = Field(default=None, description="Error message.")


class McpApprovalRequestParam(BaseModel):
    """MCP tool approval request."""

    id: str = Field(..., description="The request ID.")
    arguments: str = Field(..., description="JSON string of tool arguments.")
    name: str = Field(..., description="The tool name.")
    server_label: str = Field(..., description="The MCP server label.")
    type: Literal["mcp_approval_request"] = Field(
        ..., description="Always 'mcp_approval_request'."
    )


class McpApprovalResponseParam(BaseModel):
    """MCP approval response."""

    approval_request_id: str = Field(..., description="The request ID being answered.")
    approve: bool = Field(..., description="The approval decision.")
    type: Literal["mcp_approval_response"] = Field(
        ..., description="Always 'mcp_approval_response'."
    )
    id: str | None = Field(default=None, description="The unique ID.")
    reason: str | None = Field(default=None, description="The decision reason.")


class McpCallParam(BaseModel):
    """MCP tool invocation."""

    id: str = Field(..., description="The tool call ID.")
    arguments: str = Field(..., description="JSON string of arguments.")
    name: str = Field(..., description="The tool name.")
    server_label: str = Field(..., description="The MCP server label.")
    type: Literal["mcp_call"] = Field(..., description="Always 'mcp_call'.")
    approval_request_id: str | None = Field(
        default=None, description="For approval flow."
    )
    error: str | None = Field(default=None, description="Tool error.")
    output: str | None = Field(default=None, description="Tool output.")
    status: (
        Literal["in_progress", "completed", "incomplete", "calling", "failed"] | None
    ) = Field(default=None, description="The status.")


# =============================================================================
# Item Reference
# =============================================================================


class ItemReferenceParam(BaseModel):
    """A reference to an existing item."""

    id: str = Field(..., description="The item ID.")
    type: Literal["item_reference"] | None = Field(
        default=None, description="Always 'item_reference'."
    )


# =============================================================================
# Reasoning Item (for input)
# =============================================================================


class ReasoningItemSummaryParam(BaseModel):
    text: str = Field(..., description="A summary of the reasoning output.")
    type: Literal["summary_text"] = Field(..., description="Always 'summary_text'.")


class ReasoningItemParam(BaseModel):
    """A reasoning item for multi-turn conversations."""

    id: str = Field(..., description="The unique identifier.")
    type: Literal["reasoning"] = Field(..., description="Always 'reasoning'.")
    summary: list[ReasoningItemSummaryParam] = Field(
        default_factory=list, description="Reasoning summary."
    )
    encrypted_content: str | None = Field(
        default=None, description="Encrypted content for multi-turn."
    )


# =============================================================================
# Image Generation Call (for input)
# =============================================================================


class ImageGenerationCallParam(BaseModel):
    """An image generation call for multi-turn conversations."""

    id: str = Field(..., description="The unique ID.")
    result: str | None = Field(
        default=None, description="The generated image encoded in base64."
    )
    status: Literal["in_progress", "completed", "generating", "failed"] = Field(
        ..., description="The status."
    )
    type: Literal["image_generation_call"] = Field(
        ..., description="Always 'image_generation_call'."
    )


# =============================================================================
# ResponseInputItemParam - union of all item types that can appear in input
# =============================================================================

ResponseInputItemParam = (
    InputMessageParam
    | MessageParam
    | ResponseOutputMessageParam
    | ResponseFunctionToolCallParam
    | FunctionCallOutputParam
    | ResponseCustomToolCallParam
    | ResponseCustomToolCallOutputParam
    | ComputerCallOutputParam
    | LocalShellCallParam
    | LocalShellCallOutputParam
    | ShellCallParam
    | ShellCallOutputParam
    | ApplyPatchCallParam
    | ApplyPatchCallOutputParam
    | McpListToolsParam
    | McpApprovalRequestParam
    | McpApprovalResponseParam
    | McpCallParam
    | ReasoningItemParam
    | ImageGenerationCallParam
    | ItemReferenceParam
    | dict[str, Any]
)
ResponseInputParam = str | list[ResponseInputItemParam]

# =============================================================================
# Tool Definition Types
# =============================================================================


class FunctionToolParam(BaseModel):
    """Defines a function tool the model can call.

    Note: The Responses API uses a flat structure (name, parameters, strict, description
    at the top level), unlike the Chat Completions API which nests them under a
    ``function`` key.
    """

    name: str = Field(..., description="The name of the function to call.")
    parameters: dict[str, Any] | None = Field(
        default=None,
        description="A JSON Schema object describing the parameters of the function.",
    )
    strict: bool | None = Field(
        default=None,
        description="Whether to enforce strict parameter validation. Default true.",
    )
    type: Literal["function"] = Field(
        ..., description="The type of the function tool. Always 'function'."
    )
    description: str | None = Field(
        default=None, description="A description of the function."
    )


class FileSearchToolParam(BaseModel):
    type: Literal["file_search"] = Field(..., description="The type of the tool.")
    file_ids: list[str] | None = Field(default=None, description="Files to search.")


class WebSearchToolParam(BaseModel):
    type: Literal["web_search"] = Field(..., description="The type of the tool.")
    model_config = ConfigDict(extra="allow")


class WebSearchPreviewUserLocation(BaseModel):
    type: Literal["approximate"] = Field(..., description="Always 'approximate'.")
    city: str | None = Field(default=None, description="City name.")
    country: str | None = Field(default=None, description="ISO country code.")
    region: str | None = Field(default=None, description="Region name.")
    timezone: str | None = Field(default=None, description="IANA timezone.")


class WebSearchPreviewToolParam(BaseModel):
    type: Literal["web_search_preview", "web_search_preview_2025_03_11"] = Field(
        ..., description="The type of the tool."
    )
    search_context_size: Literal["low", "medium", "high"] | None = Field(
        default=None, description="Search context size."
    )
    user_location: WebSearchPreviewUserLocation | None = Field(
        default=None, description="User location."
    )


class CodeInterpreterContainerAuto(BaseModel):
    type: Literal["auto"] = Field(..., description="Always 'auto'.")
    file_ids: list[str] | None = Field(default=None, description="Uploaded files.")
    memory_limit: Literal["1g", "4g", "16g", "64g"] | None = Field(
        default=None, description="Memory limit."
    )


class CodeInterpreterToolParam(BaseModel):
    type: Literal["code_interpreter"] = Field(..., description="The type of the tool.")
    container: str | CodeInterpreterContainerAuto = Field(
        ..., description="The code interpreter container."
    )


class ComputerToolParam(BaseModel):
    type: Literal["computer_use_preview"] = Field(
        ..., description="The type of the tool."
    )
    model_config = ConfigDict(extra="allow")


class ImageGenerationInputImageMask(BaseModel):
    file_id: str | None = Field(default=None, description="Mask image file ID.")
    image_url: str | None = Field(default=None, description="Base64-encoded mask.")


class ImageGenerationToolParam(BaseModel):
    type: Literal["image_generation"] = Field(..., description="The type of the tool.")
    model: str | Literal["gpt-image-1", "gpt-image-1-mini"] | None = Field(
        default=None, description="The image generation model to use."
    )
    size: Literal["1024x1024", "1024x1536", "1536x1024", "auto"] | None = Field(
        default=None, description="The size of the generated image."
    )
    quality: Literal["low", "medium", "high", "auto"] | None = Field(
        default=None, description="The quality of the generated image."
    )
    background: Literal["transparent", "opaque", "auto"] | None = Field(
        default=None, description="The background of the generated image."
    )
    input_fidelity: Literal["high", "low"] | None = Field(
        default=None, description="Input fidelity."
    )
    input_image_mask: ImageGenerationInputImageMask | None = Field(
        default=None, description="Inpainting mask."
    )
    moderation: Literal["auto", "low"] | None = Field(
        default=None, description="Moderation level."
    )
    output_compression: int | None = Field(
        default=None, description="Compression level."
    )
    output_format: Literal["png", "webp", "jpeg"] | None = Field(
        default=None, description="Output format."
    )
    partial_images: int | None = Field(
        default=None, description="Partial images for streaming (0-3)."
    )


class McpAllowedToolsFilter(BaseModel):
    read_only: bool | None = Field(default=None, description="Tool is read-only.")
    tool_names: list[str] | None = Field(
        default=None, description="Allowed tool names."
    )


class McpApprovalFilter(BaseModel):
    always: McpAllowedToolsFilter | None = Field(
        default=None, description="Always require approval."
    )
    never: McpAllowedToolsFilter | None = Field(
        default=None, description="Never require approval."
    )


class McpToolParam(BaseModel):
    """MCP (Model Context Protocol) tool configuration."""

    type: Literal["mcp"] = Field(..., description="The type of the tool.")
    server_label: str = Field(..., description="Label for the MCP server.")
    server_url: str | None = Field(default=None, description="URL for the MCP server.")
    connector_id: str | None = Field(default=None, description="Service connector ID.")
    allowed_tools: list[str] | McpAllowedToolsFilter | None = Field(
        default=None, description="Allowed tools filter."
    )
    require_approval: Literal["always", "never"] | McpApprovalFilter | None = Field(
        default=None, description="Approval requirement."
    )
    authorization: str | None = Field(default=None, description="OAuth access token.")
    headers: dict[str, str] | None = Field(
        default=None, description="Custom HTTP headers."
    )
    server_description: str | None = Field(
        default=None, description="MCP server description."
    )


class LocalShellToolParam(BaseModel):
    type: Literal["local_shell"] = Field(..., description="The type of the tool.")


class FunctionShellToolParam(BaseModel):
    type: Literal["function_shell"] = Field(..., description="The type of the tool.")


class CustomToolParam(BaseModel):
    """Custom tool with grammar-based input format."""

    type: Literal["custom"] = Field(..., description="The type of the tool.")
    name: str = Field(..., description="The custom tool name.")
    description: str | None = Field(default=None, description="Tool description.")
    format: dict[str, Any] | None = Field(
        default=None, description="Input format specification."
    )


class ApplyPatchToolParam(BaseModel):
    type: Literal["apply_patch"] = Field(..., description="The type of the tool.")


ToolParam = (
    FunctionToolParam
    | FileSearchToolParam
    | WebSearchToolParam
    | WebSearchPreviewToolParam
    | CodeInterpreterToolParam
    | ComputerToolParam
    | ImageGenerationToolParam
    | McpToolParam
    | LocalShellToolParam
    | FunctionShellToolParam
    | CustomToolParam
    | ApplyPatchToolParam
    | dict[str, Any]
)

# =============================================================================
# Tool Choice Types
# =============================================================================


class ToolChoiceNoneParam(BaseModel):
    type: Literal["none"] = Field(..., description="The model will not use any tools.")


class ToolChoiceAutoParam(BaseModel):
    type: Literal["auto"] = Field(
        ..., description="The model will automatically decide whether to use tools."
    )


class ToolChoiceRequiredParam(BaseModel):
    type: Literal["required"] = Field(
        ..., description="The model must use at least one tool."
    )


class ToolChoiceFunctionParam(BaseModel):
    type: Literal["function"] = Field(
        ..., description="The model will use the specified function."
    )
    name: str = Field(..., description="The name of the function to use.")


ToolChoiceParam = Annotated[
    ToolChoiceNoneParam
    | ToolChoiceAutoParam
    | ToolChoiceRequiredParam
    | ToolChoiceFunctionParam,
    Field(discriminator="type"),
]

# =============================================================================
# Text Config Types
# =============================================================================


class TextConfigJSONSchemaParam(BaseModel):
    type: Literal["json_schema"] = Field(..., description="Structured JSON output.")
    name: str = Field(..., description="The name of the schema.")
    description: str | None = Field(
        default=None, description="A description of the schema."
    )
    schema_: dict[str, Any] = Field(..., alias="schema", description="The JSON schema.")
    strict: bool | None = Field(
        default=None,
        description="Whether to enable strict schema adherence when generating the output.",
    )

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class TextConfigJSONObjectParam(BaseModel):
    type: Literal["json_object"] = Field(..., description="JSON object output.")


class TextConfigTextParam(BaseModel):
    type: Literal["text"] = Field(..., description="Plain text output.")


TextFormatParam = Annotated[
    TextConfigJSONSchemaParam | TextConfigJSONObjectParam | TextConfigTextParam,
    Field(discriminator="type"),
]


class ResponseTextConfigParam(BaseModel):
    format: TextFormatParam | None = Field(
        default=None, description="The format of the text response."
    )


# =============================================================================
# Conversation and Prompt Types
# =============================================================================


class ConversationParam(BaseModel):
    id: str = Field(..., description="The unique ID of the conversation.")


class ResponsePromptParam(BaseModel):
    id: str = Field(..., description="The unique ID of the prompt template.")
    variables: dict[str, str] | None = Field(
        default=None, description="Variables to substitute in the prompt template."
    )


# =============================================================================
# Reasoning Config Types
# =============================================================================


class ReasoningParam(BaseModel):
    effort: Literal["none", "low", "medium", "high", "xhigh"] | None = Field(
        default=None, description="The reasoning effort level."
    )
    generate_summary: Literal["auto", "concise", "detailed"] | None = Field(
        default=None, description="Whether to generate a summary of the reasoning."
    )


# =============================================================================
# Stream Options
# =============================================================================


class StreamOptionsParam(BaseModel):
    include_usage: bool | None = Field(
        default=None,
        description="If set, an additional chunk will be streamed with usage statistics.",
    )


# =============================================================================
# Main Request Class
# =============================================================================


class ResponsesRequest(BaseModel):
    """OpenAI Responses API request. See https://platform.openai.com/docs/api-reference/responses."""

    model: str = Field(
        ...,
        description="Model ID used to generate the response, like 'gpt-4o' or 'o3'.",
    )
    background: bool | None = Field(
        default=None,
        description="Whether to run the model response in the background.",
    )
    conversation: str | ConversationParam | None = Field(
        default=None,
        description="The conversation that this response belongs to.",
    )
    include: list[str] | None = Field(
        default=None,
        description="Specify additional output data to include in the model response.",
    )
    input: ResponseInputParam | None = Field(
        default=None,
        description="Text, image, or file inputs to the model, used to generate a response.",
    )
    instructions: str | None = Field(
        default=None,
        description="A system (or developer) message inserted into the model's context.",
    )
    max_output_tokens: int | None = Field(
        default=None,
        description="An upper bound for the number of tokens that can be generated for a response.",
    )
    max_tool_calls: int | None = Field(
        default=None,
        description="The maximum number of total calls to built-in tools.",
    )
    metadata: dict[str, str] | None = Field(
        default=None,
        description="Set of 16 key-value pairs that can be attached to an object.",
    )
    parallel_tool_calls: bool | None = Field(
        default=None,
        description="Whether to allow the model to run tool calls in parallel.",
    )
    previous_response_id: str | None = Field(
        default=None,
        description="The unique ID of the previous response to the model.",
    )
    prompt: ResponsePromptParam | None = Field(
        default=None,
        description="Reference to a prompt template and its variables.",
    )
    prompt_cache_key: str | None = Field(
        default=None,
        description="Used by OpenAI to cache responses for similar requests.",
    )
    prompt_cache_retention: Literal["in-memory", "24h"] | None = Field(
        default=None,
        description="Retention policy for prompt cache.",
    )
    reasoning: ReasoningParam | None = Field(
        default=None,
        description="Configuration options for reasoning models.",
    )
    safety_identifier: str | None = Field(
        default=None,
        description="A stable identifier used to help detect users violating usage policies.",
    )
    service_tier: Literal["auto", "default", "flex", "scale", "priority"] | None = (
        Field(
            default=None,
            description="Specifies the processing type used for serving the request.",
        )
    )
    store: bool | None = Field(
        default=None,
        description="Whether to store the generated model response for later retrieval via API.",
    )
    stream: bool | None = Field(
        default=None,
        description="If set to true, the model response data will be streamed.",
    )
    stream_options: StreamOptionsParam | None = Field(
        default=None, description="Options for streaming responses."
    )
    temperature: float | None = Field(
        default=None,
        description="Sampling temperature (0-2). Higher values make output more random.",
    )
    text: ResponseTextConfigParam | None = Field(
        default=None,
        description="Configuration options for a text response from the model.",
    )
    tool_choice: (
        Literal["none", "auto", "required"] | ToolChoiceFunctionParam | None
    ) = Field(
        default=None, description="How the model should select which tool to use."
    )
    tools: list[ToolParam] | None = Field(
        default=None,
        description="An array of tools the model may call while generating a response.",
    )
    top_logprobs: int | None = Field(
        default=None,
        description="Number of most likely tokens to return at each position (0-20).",
    )
    top_p: float | None = Field(
        default=None,
        description="Nucleus sampling parameter.",
    )
    truncation: Literal["auto", "disabled"] | None = Field(
        default=None,
        description="The truncation strategy to use for the model response.",
    )
    user: str | None = Field(
        default=None,
        description="Deprecated: use safety_identifier and prompt_cache_key.",
    )
    timeout: float | None = Field(
        default=None,
        description="Client-side timeout in seconds.",
    )

    model_config = ConfigDict(extra="ignore")
