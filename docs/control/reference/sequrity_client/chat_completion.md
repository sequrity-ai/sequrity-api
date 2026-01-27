# Chat Completion

The chat completion API provides an OpenAI-compatible interface for secure LLM interactions.



::: sequrity.control.chat_completion.create_chat_completion_sync
    options:
      show_root_heading: true
      show_source: false

---


::: sequrity.types.chat_completion.request.ChatCompletionRequest
    options:
      show_root_heading: true
      show_source: true


::: sequrity.types.chat_completion.request.Message
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.request.SystemMessage
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.request.UserMessage
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.request.AssistantMessage
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.request.ToolMessage
    options:
      show_root_heading: true
      show_source: false


::: sequrity.types.chat_completion.request.Tool
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.request.FunctionDefinition
    options:
      show_root_heading: true
      show_source: false


::: sequrity.types.chat_completion.request.ResponseFormat
    options:
      show_root_heading: true
      show_source: false

---


::: sequrity.types.chat_completion.response.ChatCompletionResponse
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.response.Choice
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.response.ResponseMessage
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.response.ResponseToolCall
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.chat_completion.response.CompletionUsage
    options:
      show_root_heading: true
      show_source: false

---

## Result Schema

When using Dual-LLM mode, the response content follows `ResponseContentJsonSchema`.

::: sequrity.control.types.results.ResponseContentJsonSchema
    options:
      show_root_heading: true
      show_source: true

::: sequrity.control.types.results.ErrorInfo
    options:
      show_root_heading: true
      show_source: true
