# Responses API

The Responses API provides an OpenAI Responses-compatible interface for secure LLM interactions. It supports function calling, multi-turn conversations via `previous_response_id`, reasoning models, and streaming.

::: sequrity.control.resources.responses.ResponsesResource
    options:
      show_root_heading: true
      show_source: false

---

## Request Types

::: sequrity.types.responses.request.ResponsesRequest
    options:
      show_root_heading: true
      show_source: true

### Input Types

::: sequrity.types.responses.request.InputMessageParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.InputTextParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.InputImageParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.InputFileParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.InputAudioParam
    options:
      show_root_heading: true
      show_source: false

### Multi-turn Input Types

::: sequrity.types.responses.request.FunctionCallOutputParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.ResponseOutputMessageParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.ResponseFunctionToolCallParam
    options:
      show_root_heading: true
      show_source: false

### Tool Definitions

::: sequrity.types.responses.request.FunctionToolParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.WebSearchPreviewToolParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.CodeInterpreterToolParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.McpToolParam
    options:
      show_root_heading: true
      show_source: false

### Tool Choice

::: sequrity.types.responses.request.ToolChoiceFunctionParam
    options:
      show_root_heading: true
      show_source: false

### Text Config

::: sequrity.types.responses.request.ResponseTextConfigParam
    options:
      show_root_heading: true
      show_source: false

### Reasoning Config

::: sequrity.types.responses.request.ReasoningParam
    options:
      show_root_heading: true
      show_source: false

### Other Config Types

::: sequrity.types.responses.request.ConversationParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.ResponsePromptParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.request.StreamOptionsParam
    options:
      show_root_heading: true
      show_source: false

---

## Response Types

::: sequrity.types.responses.response.ResponsesResponse
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.response.ResponseOutputMessage
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.response.OutputText
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.response.Refusal
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.response.FunctionToolCall
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.response.ReasoningItem
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.response.ResponseUsage
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.responses.response.ResponseError
    options:
      show_root_heading: true
      show_source: false

---

## Result Schema

When using Dual-LLM mode, the response content follows `ResponseContentJsonSchema`.

::: sequrity.control.types.dual_llm_response.ResponseContentJsonSchema
    options:
      show_root_heading: true
      show_source: true

::: sequrity.control.types.dual_llm_response.ErrorInfo
    options:
      show_root_heading: true
      show_source: true
