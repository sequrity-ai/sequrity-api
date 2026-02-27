# Responses API

The Sequrity Control Responses API is compatible with the [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses). This allows you to use Sequrity's security features while maintaining compatibility with existing OpenAI Responses-based applications.

For the Chat Completions format, see the [Chat Completion API](./chat_completion.md) reference. For the Anthropic Messages format, see the [Messages API](./messages.md) reference.

## Endpoints

| Endpoint | Provider |
|----------|----------|
| `POST /control/{endpoint_type}/v1/responses` | Default |
| `POST /control/{endpoint_type}/openai/v1/responses` | OpenAI |
| `POST /control/{endpoint_type}/sequrity_azure/v1/responses` | Sequrity Azure |

Where `{endpoint_type}` is `chat`, `code`, `agent`, or `lang-graph`. See [URL Pattern](./index.md#url-pattern) and [Service Providers](../../../general/rest_api/service_provider.md).

## Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | `string` | Yes | Model ID, e.g. `gpt-4o`, `o3`. |
| `input` | `string | array[InputItem]` | No | Text, image, or file inputs to the model. See [Input Types](#input-types). |
| `instructions` | `string` | No | A system (or developer) message inserted into the model's context. |
| `tools` | `array[Tool]` | No | Tools the model may call. See [Tools](#tools). |
| `tool_choice` | `string | object` | No | How the model should select which tool to use: `"none"`, `"auto"`, `"required"`, or a function object. |
| `stream` | `boolean` | No | If `true`, the response is streamed as server-sent events. |
| `temperature` | `float` | No | Sampling temperature (0–2). Higher values produce more random output. |
| `top_p` | `float` | No | Nucleus sampling parameter. |
| `max_output_tokens` | `integer` | No | Upper bound for generated tokens. |
| `reasoning` | `object` | No | Configuration for reasoning models. See [Reasoning](#reasoning). |
| `text` | `object` | No | Text response format configuration. See [Text Config](#text-config). |
| `metadata` | `object` | No | Key-value pairs (up to 16) attached to the response. |
| `previous_response_id` | `string` | No | ID of a previous response for multi-turn conversations. |
| `include` | `array[string]` | No | Additional output data to include in the response. |
| `store` | `boolean` | No | Whether to store the response for later retrieval. |
| `truncation` | `string` | No | Truncation strategy: `"auto"` or `"disabled"`. |
| `parallel_tool_calls` | `boolean` | No | Whether to allow parallel tool execution. |
| `max_tool_calls` | `integer` | No | Maximum number of calls to built-in tools. |
| `background` | `boolean` | No | Whether to run the response in the background. |
| `conversation` | `string | object` | No | Conversation context. |
| `prompt` | `object` | No | Prompt template reference with `id` and optional `variables`. |
| `service_tier` | `string` | No | Processing tier: `"auto"`, `"default"`, `"flex"`, `"scale"`, `"priority"`. |
| `stream_options` | `object` | No | Options for streaming responses (e.g., `include_usage`). |
| `top_logprobs` | `integer` | No | Number of most likely tokens to return at each position (0–20). |
| `timeout` | `float` | No | Client-side timeout in seconds. |

### Input Types

The `input` field accepts either a plain string or an array of input items. Input items are distinguished by `role` or `type`:

#### Input Message

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | `"user" | "system" | "developer"` | Yes | The role of the message. |
| `content` | `string | array[ContentItem]` | Yes | Message content (text, images, files, or audio). |

#### Content Item Types

| Type | Key Fields | Description |
|------|------------|-------------|
| `input_text` | `type`, `text` | Plain text input. |
| `input_image` | `type`, `detail`, `file_id`, `image_url` | Image via URL, base64, or file ID. Detail: `"auto"`, `"low"`, `"high"`. |
| `input_file` | `type`, `file_id` | File via file ID. |
| `input_audio` | `type`, `audio` | Base64-encoded audio data. |

#### Function Call Output (for multi-turn)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"function_call_output"` | Yes | |
| `call_id` | `string` | Yes | The tool call ID from the model's function call. |
| `output` | `string` | Yes | The text output from the tool execution. |

### Tools

The Responses API supports multiple tool types:

#### Function Tool

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"function"` | Yes | |
| `name` | `string` | Yes | The function name. |
| `parameters` | `object` | No | JSON Schema describing the function parameters. |
| `description` | `string` | No | Description of the function. |
| `strict` | `boolean` | No | Enforce strict parameter validation. |

#### Other Tool Types

| Type | Description |
|------|-------------|
| `file_search` | Search uploaded files. |
| `web_search_preview` | Web search with user location support. |
| `code_interpreter` | Execute code in a sandbox. |
| `computer_use_preview` | Computer use tool. |
| `image_generation` | Generate images. |
| `mcp` | Model Context Protocol server tools. |
| `web_search` | Web search tool. |
| `local_shell` | Local shell execution tool. |
| `custom` | Custom tool type. |

### Reasoning

| Field | Type | Description |
|-------|------|-------------|
| `effort` | `string` | Reasoning effort level: `"none"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`. |
| `generate_summary` | `string` | Summary generation: `"auto"`, `"concise"`, `"detailed"`. |

### Text Config

| Field | Type | Description |
|-------|------|-------------|
| `format.type` | `string` | Output format: `"text"`, `"json_object"`, or `"json_schema"`. |
| `format.name` | `string` | Schema name (for `json_schema`). |
| `format.schema` | `object` | JSON Schema (for `json_schema`). |
| `format.strict` | `boolean` | Strict schema adherence (for `json_schema`). |

## Response Body

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier for this response. |
| `object` | `"response"` | Always `"response"`. |
| `created_at` | `float` | Unix timestamp (seconds) when created. |
| `model` | `string` | The model used. |
| `output` | `array[OutputItem]` | Generated content items. See [Output Items](#output-items). |
| `status` | `string` | Response status: `"completed"`, `"failed"`, `"in_progress"`, `"cancelled"`, `"queued"`, `"incomplete"`. |
| `error` | `object | null` | Error information with `code` and `message` fields. |
| `usage` | `ResponseUsage` | Token usage statistics. |
| `parallel_tool_calls` | `boolean` | Whether parallel tool calls were enabled. |
| `tool_choice` | `string | object` | Tool choice used for this response. |
| `tools` | `array[object]` | Tools available for this response. |
| `incomplete_details` | `object | null` | Details on why the response is incomplete. |
| `temperature` | `float | null` | Sampling temperature used. |
| `top_p` | `float | null` | Nucleus sampling used. |
| `max_output_tokens` | `integer | null` | Max output tokens setting. |
| `truncation` | `string | null` | Truncation strategy used. |
| `service_tier` | `string | null` | Service tier used. |

### Output Items

Output items are distinguished by the `type` field:

#### Message (`type: "message"`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique ID of the output message. |
| `type` | `"message"` | |
| `role` | `"assistant"` | Always `"assistant"`. |
| `content` | `array[ContentItem]` | Content items: `output_text` (with `text` and `annotations`) or `refusal`. |
| `status` | `string` | `"in_progress"`, `"completed"`, `"incomplete"`. |

#### Function Call (`type: "function_call"`)

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"function_call"` | |
| `call_id` | `string` | Unique ID for responding with tool output. |
| `name` | `string` | The function name. |
| `arguments` | `string` | JSON-encoded arguments. |
| `id` | `string | null` | Unique ID of the tool call. |
| `status` | `string | null` | `"in_progress"`, `"completed"`, `"incomplete"`. |

#### Reasoning (`type: "reasoning"`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique ID of the reasoning item. |
| `type` | `"reasoning"` | |
| `summary` | `array[object]` | Reasoning summary text items. |
| `encrypted_content` | `string | null` | Encrypted content for multi-turn continuity. |

#### Other Output Item Types

| Type | Description |
|------|-------------|
| `file_search_call` | File search tool call results. |
| `web_search_call` | Web search tool call results. |
| `code_interpreter_call` | Code interpreter execution results. |
| `computer_call` | Computer use tool call. |
| `image_generation_call` | Image generation results. |
| `local_shell_call` | Local shell execution results. |
| `mcp_call` | MCP server tool call results. |
| `mcp_list_tools` | MCP tool listing results. |
| `mcp_approval_request` | MCP approval request. |
| `custom_tool_call` | Custom tool call results. |

### ResponseUsage

| Field | Type | Description |
|-------|------|-------------|
| `input_tokens` | `integer` | Input tokens used. |
| `input_tokens_details.cached_tokens` | `integer` | Tokens retrieved from cache. |
| `output_tokens` | `integer` | Output tokens generated. |
| `output_tokens_details.reasoning_tokens` | `integer` | Reasoning tokens used. |
| `total_tokens` | `integer` | Total tokens used. |

## Streaming Events

When `stream` is `true`, the response is delivered as server-sent events. Each event has a `type` field:

### Lifecycle Events

| Event Type | Description |
|------------|-------------|
| `response.created` | Emitted once when the response is first created. |
| `response.in_progress` | Response transitions to in-progress state. |
| `response.completed` | Response completes successfully. |
| `response.failed` | Response fails. |
| `response.incomplete` | Response is incomplete (e.g. max tokens reached). |

### Structure Events

| Event Type | Description |
|------------|-------------|
| `response.output_item.added` | A new output item (message, reasoning, function_call) starts. |
| `response.output_item.done` | An output item is fully completed. |
| `response.content_part.added` | A new content part starts within a message. |
| `response.content_part.done` | A content part is completed. |

### Content Events

| Event Type | Key Fields | Description |
|------------|------------|-------------|
| `response.output_text.delta` | `delta` | Incremental text content. |
| `response.output_text.done` | `text` | Text content finalized. |
| `response.function_call_arguments.delta` | `delta` | Incremental function call arguments. |
| `response.function_call_arguments.done` | `name`, `arguments` | Function call arguments finalized. |

### Reasoning Events

| Event Type | Description |
|------------|-------------|
| `response.reasoning_summary_part.added` | A new reasoning summary part starts. |
| `response.reasoning_summary_part.done` | A reasoning summary part completes. |
| `response.reasoning_summary_text.delta` | Incremental reasoning summary text. |
| `response.reasoning_summary_text.done` | Reasoning summary text finalized. |

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
