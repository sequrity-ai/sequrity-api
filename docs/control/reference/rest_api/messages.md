# Messages API

The Sequrity Control Messages API is compatible with the [Anthropic Messages API](https://docs.anthropic.com/en/api/messages). This allows you to use Sequrity's security features while maintaining compatibility with existing Anthropic-based applications.

For the OpenAI Chat Completions format, see the [Chat Completion API](./chat_completion.md) reference.

## Endpoints

| Endpoint | Provider |
|----------|----------|
| `POST /control/{endpoint_type}/v1/messages` | Default |
| `POST /control/{endpoint_type}/anthropic/v1/messages` | Anthropic |

Where `{endpoint_type}` is `chat`, `code`, `agent`, or `lang-graph`. See [URL Pattern](./index.md#url-pattern) and [Service Providers](../../../general/rest_api/service_provider.md).

## Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | `array[MessageParam]` | Yes | Input messages with alternating `user` and `assistant` turns. See [Messages](#messages). |
| `model` | `string` | Yes | Model ID, e.g. `claude-4-sonnet`. For Dual-LLM, specify two models separated by a comma (`pllm,qllm`). |
| `max_tokens` | `integer` | Yes | Maximum number of tokens to generate before stopping. |
| `system` | `string \| array[TextBlockParam]` | No | System prompt providing context and instructions. |
| `temperature` | `float` | No | Sampling randomness (0.0–1.0). |
| `top_p` | `float` | No | Nucleus sampling probability threshold. |
| `top_k` | `integer` | No | Only sample from the top K options for each token. |
| `tools` | `array[ToolParam]` | No | Tool definitions the model may use. See [Tools](#tools). |
| `tool_choice` | `ToolChoice` | No | How the model should use tools. See [Tool Choice](#tool-choice). |
| `thinking` | `ThinkingConfig` | No | Extended thinking configuration. See [Thinking](#thinking). |
| `stop_sequences` | `array[string]` | No | Custom stop sequences. |
| `stream` | `boolean` | No | If `true`, stream the response via server-sent events. |
| `output_config` | `OutputConfig` | No | Output format configuration (e.g. JSON schema). |
| `metadata` | `object` | No | Request metadata. Supports `user_id` for tracking. |
| `service_tier` | `string` | No | `"auto"` or `"standard_only"`. |
| `timeout` | `float` | No | Maximum request duration in seconds. |

### Messages

Each message has a `role` (`"user"` or `"assistant"`) and `content` (a string or array of content blocks).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | `"user" \| "assistant"` | Yes | The message author. |
| `content` | `string \| array[ContentBlock]` | Yes | Message content. See [Content Blocks](#content-blocks). |

### Content Blocks

Content blocks are distinguished by the `type` field.

#### Text Block

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"text"` | Yes | |
| `text` | `string` | Yes | The text content. |
| `cache_control` | `object` | No | Cache control breakpoint. |
| `citations` | `array` | No | Citations supporting the text. |

#### Image Block

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"image"` | Yes | |
| `source` | `ImageSource` | Yes | Base64 (`type: "base64"`, `media_type`, `data`) or URL (`type: "url"`, `url`). |
| `cache_control` | `object` | No | Cache control breakpoint. |

#### Document Block

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"document"` | Yes | |
| `source.type` | `"base64"` | Yes | |
| `source.media_type` | `"application/pdf"` | Yes | |
| `source.data` | `string` | Yes | Base64-encoded PDF data. |
| `cache_control` | `object` | No | Cache control breakpoint. |

#### Tool Use Block (in assistant messages)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"tool_use"` | Yes | |
| `id` | `string` | Yes | Unique tool use ID. |
| `name` | `string` | Yes | Tool name. |
| `input` | `object` | Yes | Input arguments for the tool. |
| `cache_control` | `object` | No | Cache control breakpoint. |

#### Tool Result Block (in user messages)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"tool_result"` | Yes | |
| `tool_use_id` | `string` | Yes | ID of the tool use this responds to. |
| `content` | `string \| array[TextBlock \| ImageBlock \| DocumentBlock]` | No | The tool result. |
| `is_error` | `boolean` | No | `true` if the tool execution errored. |
| `cache_control` | `object` | No | Cache control breakpoint. |

#### Thinking Block (in assistant messages)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"thinking"` | Yes | |
| `text` | `string` | Yes | The model's thinking content. |
| `cache_control` | `object` | No | Cache control breakpoint. |

### Tools

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Tool name. |
| `input_schema` | `object` | Yes | JSON Schema describing the tool's input parameters. |
| `description` | `string` | No | Detailed description of what the tool does. |
| `cache_control` | `object` | No | Cache control breakpoint. |
| `strict` | `boolean` | No | Guarantee schema validation on tool inputs. |
| `type` | `"custom"` | No | Tool type. |

### Tool Choice

Tool choice controls how the model uses tools. Discriminated by `type`:

| Type | Description |
|------|-------------|
| `auto` | Model decides whether to use tools. Optional: `disable_parallel_tool_use`. |
| `any` | Model must use at least one tool. Optional: `disable_parallel_tool_use`. |
| `tool` | Model must use the named tool. Required: `name`. Optional: `disable_parallel_tool_use`. |
| `none` | Model will not use tools. |

### Thinking

Extended thinking configuration. Discriminated by `type`:

| Type | Fields | Description |
|------|--------|-------------|
| `enabled` | `budget_tokens` (int, min 1024) | Enable thinking with a token budget. |
| `disabled` | — | Disable thinking. |

### Output Config

| Field | Type | Description |
|-------|------|-------------|
| `format.type` | `"json_schema"` | Output format type. |
| `format.schema` | `object` | JSON Schema for structured output. |

## Response Body

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique object identifier. |
| `type` | `"message"` | Always `"message"`. |
| `role` | `"assistant"` | Always `"assistant"`. |
| `content` | `array[ContentBlock]` | Generated content blocks. See [Response Content Blocks](#response-content-blocks). |
| `model` | `string` | The model that handled the request. |
| `stop_reason` | `string \| null` | Why generation stopped: `"end_turn"`, `"max_tokens"`, `"stop_sequence"`, `"tool_use"`, `"pause_turn"`, `"refusal"`. |
| `stop_sequence` | `string \| null` | Which stop sequence was hit, if any. |
| `usage` | `Usage` | Token usage statistics. |

### Response Content Blocks

| Type | Key Fields | Description |
|------|------------|-------------|
| `text` | `text`, `citations` | Text content with optional citations. |
| `thinking` | `text` | Model's reasoning process. |
| `redacted_thinking` | — | Redacted thinking content. |
| `tool_use` | `id`, `name`, `input` | The model wants to call a tool. |
| `server_tool_use` | `id`, `name` | Server-side tool use (e.g. web search). |
| `web_search_tool_result` | — | Web search results. |

### Usage

| Field | Type | Description |
|-------|------|-------------|
| `input_tokens` | `integer` | Input tokens used. |
| `output_tokens` | `integer` | Output tokens generated. |
| `cache_creation_input_tokens` | `integer \| null` | Tokens used to create cache. |
| `cache_read_input_tokens` | `integer \| null` | Tokens read from cache. |
| `cache_creation` | `object \| null` | Breakdown of cached tokens by TTL. |
| `server_tool_use` | `object \| null` | Server tool usage stats. |
| `service_tier` | `string \| null` | `"standard"`, `"priority"`, or `"batch"`. |

## Headers

See [Custom Headers](./index.md#custom-headers) for the full list. Summary:

| Header | Direction | Description |
|--------|-----------|-------------|
| `Authorization` | Request | `Bearer <sequrity-api-key>` |
| `X-Api-Key` | Request | LLM provider API key (BYOK). |
| `X-Features` | Request | [Security features](./headers/security_features.md) (agent arch, classifiers, blockers). |
| `X-Policy` | Request | [Security policy](./headers/security_policy.md) (SQRT rules). |
| `X-Config` | Request | [Fine-grained config](./headers/security_config.md) (FSM, prompts, response format). |
| `X-Session-ID` | Request | Explicit session ID for multi-turn conversations. |
| `X-Session-ID` | Response | Session ID assigned by the server. |
