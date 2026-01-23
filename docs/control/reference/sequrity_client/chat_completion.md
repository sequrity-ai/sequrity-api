# Chat Completion

The chat completion API provides an OpenAI-compatible interface for secure LLM interactions.


## Core Function

::: sequrity_api.control.chat_completion.create_chat_completion_sync
    options:
      show_root_heading: true
      show_source: true

---

## Request Types

### ChatCompletionRequest

::: sequrity_api.types.chat_completion.request.ChatCompletionRequest
    options:
      show_root_heading: true
      show_source: false

### Message Types

::: sequrity_api.types.chat_completion.request.Message
    options:
      show_root_heading: true
      show_source: false

::: sequrity_api.types.chat_completion.request.SystemMessage
    options:
      show_root_heading: true
      show_source: false

::: sequrity_api.types.chat_completion.request.UserMessage
    options:
      show_root_heading: true
      show_source: false

::: sequrity_api.types.chat_completion.request.AssistantMessage
    options:
      show_root_heading: true
      show_source: false

::: sequrity_api.types.chat_completion.request.ToolMessage
    options:
      show_root_heading: true
      show_source: false

### Tool Definition

::: sequrity_api.types.chat_completion.request.Tool
    options:
      show_root_heading: true
      show_source: false

::: sequrity_api.types.chat_completion.request.FunctionDefinition
    options:
      show_root_heading: true
      show_source: false

### Response Format

::: sequrity_api.types.chat_completion.request.ResponseFormat
    options:
      show_root_heading: true
      show_source: false

---

## Response Types

### ChatCompletionResponse

::: sequrity_api.types.chat_completion.response.ChatCompletionResponse
    options:
      show_root_heading: true
      show_source: false

### Choice

::: sequrity_api.types.chat_completion.response.Choice
    options:
      show_root_heading: true
      show_source: false

### ResponseMessage

::: sequrity_api.types.chat_completion.response.ResponseMessage
    options:
      show_root_heading: true
      show_source: false

### Tool Calls

::: sequrity_api.types.chat_completion.response.ResponseToolCall
    options:
      show_root_heading: true
      show_source: false

### Usage

::: sequrity_api.types.chat_completion.response.CompletionUsage
    options:
      show_root_heading: true
      show_source: false

---

## Result Schema

When using Dual-LLM mode, the response content follows `ResponseContentJsonSchema`.

::: sequrity_api.types.control.results.ResponseContentJsonSchema
    options:
      show_root_heading: true
      show_source: true

::: sequrity_api.types.control.results.ErrorInfo
    options:
      show_root_heading: true
      show_source: true
