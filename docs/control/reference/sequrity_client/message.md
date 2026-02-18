# Anthropic Messages API

The Messages API provides an Anthropic-compatible interface for secure LLM interactions using the Messages format.

::: sequrity.control.resources.messages.MessagesResource
    options:
      show_root_heading: true
      show_source: false

---

## Request Types

::: sequrity.types.messages.request.AnthropicMessageRequest
    options:
      show_root_heading: true
      show_source: true

::: sequrity.types.messages.request.MessageParam
    options:
      show_root_heading: true
      show_source: false

### Content Blocks

::: sequrity.types.messages.request.TextBlockParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ImageBlockParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.DocumentBlockParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ToolUseBlockParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ToolResultBlockParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ThinkingBlockParam
    options:
      show_root_heading: true
      show_source: false

### Tool Types

::: sequrity.types.messages.request.ToolParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ToolInputSchema
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ToolChoiceAutoParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ToolChoiceAnyParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ToolChoiceToolParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ToolChoiceNoneParam
    options:
      show_root_heading: true
      show_source: false

### Thinking Configuration

::: sequrity.types.messages.request.ThinkingConfigEnabledParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.ThinkingConfigDisabledParam
    options:
      show_root_heading: true
      show_source: false

### Output Configuration

::: sequrity.types.messages.request.OutputConfigParam
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.request.JSONOutputFormatParam
    options:
      show_root_heading: true
      show_source: false

---

## Response Types

::: sequrity.types.messages.response.AnthropicMessageResponse
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.response.TextBlock
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.response.ThinkingBlock
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.response.ToolUseBlock
    options:
      show_root_heading: true
      show_source: false

::: sequrity.types.messages.response.Usage
    options:
      show_root_heading: true
      show_source: false
