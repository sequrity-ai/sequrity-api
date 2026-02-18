# X-Config

The `X-Config` header is a JSON object that provides additional product configuration settings.

This header is **optional** and can be used in Headers-Only Mode to fine-tune session behavior.

## Data Structure

```json
{
  "fsm": {
    "min_num_tools_for_filtering": 10,
    "clear_session_meta": "never",
    "max_n_turns": 5,
    "clear_history_every_n_attempts": null,
    "disable_rllm": true,
    "enable_multistep_planning": false,
    "enabled_internal_tools": ["parse_with_ai", "verify_hypothesis"],
    "prune_failed_steps": false,
    "force_to_cache": [],
    "max_pllm_steps": null,
    "max_tool_calls_per_step": null,
    "reduced_grammar_for_rllm_review": true,
    "retry_on_policy_violation": false,
    "wrap_tool_result": null,
    "detect_tool_errors": null,
    "detect_tool_error_regex_pattern": null,
    "detect_tool_error_max_result_length": null,
    "strict_tool_result_parsing": null
  },
  "prompt": {
    "flavor": null,
    "version": null,
    "pllm": {
      "debug_info_level": "normal",
      "clarify_ambiguous_queries": null,
      "context_var_visibility": null,
      "query_inline_roles": null,
      "query_role_name_overrides": null,
      "query_include_tool_calls": null,
      "query_include_tool_args": null,
      "query_include_tool_results": null
    },
    "rllm": {
      "debug_info_level": null
    }
  },
  "response_format": {
    "strip_response_content": false,
    "include_program": false,
    "include_policy_check_history": false,
    "include_namespace_snapshot": false
  }
}
```

## Top-Level Fields

The configuration is organized into three sections:

- **`fsm`**: FSM (Finite State Machine) overrides for execution behavior
- **`prompt`**: Per-LLM prompt configuration overrides
- **`response_format`**: Response format and content settings

All fields are optional and have sensible defaults.

---

## FSM Overrides (`fsm`)

### Shared Fields (Single-LLM & Dual-LLM)

#### `fsm.min_num_tools_for_filtering`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `10` | >= 2 |

Minimum number of available tools to trigger tool filtering. If fewer tools are available, no filtering is performed.

#### `fsm.clear_session_meta`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"never"` |

When to clear session metadata:

- `"never"`: Never clear
- `"every_attempt"`: Clear at the beginning of each PLLM attempt
- `"every_turn"`: Clear at the beginning of each turn

#### `fsm.max_n_turns`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `5` | >= 1 |

Maximum number of conversation turns allowed in the session.

### Dual-LLM Only Fields

#### `fsm.max_pllm_steps`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `null` | >= 1 |

Maximum number of PLLM steps before giving up and returning an error.

#### `fsm.max_tool_calls_per_step`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `null` | >= 1 |

Maximum number of tool calls allowed per PLLM step.

#### `fsm.clear_history_every_n_attempts`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `null` | >= 1 |

If set, clears the tool call history every n PLLM attempts to save token usage.

#### `fsm.retry_on_policy_violation`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Retry PLLM attempts when a policy violation is detected.

#### `fsm.disable_rllm`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Disable the Response LLM (RLLM) for reviewing final responses.

#### `fsm.reduced_grammar_for_rllm_review`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Use reduced grammar for the RLLM review process.

#### `fsm.enable_multistep_planning`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Enable multi-step planning for complex user queries.

#### `fsm.prune_failed_steps`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Prune failed PLLM steps from session history to save tokens.

#### `fsm.enabled_internal_tools`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `["parse_with_ai", "verify_hypothesis"]` |

Internal tools to enable. Valid values: `"parse_with_ai"`, `"verify_hypothesis"`.

#### `fsm.force_to_cache`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `[]` |

List of tool ID regex patterns to always cache.

#### `fsm.wrap_tool_result`

| Type | Required | Default |
|------|----------|---------|
| `boolean` or `null` | No | `null` |

Whether to wrap tool results before passing to PLLM.

#### `fsm.detect_tool_errors`

| Type | Required | Default |
|------|----------|---------|
| `string` or `null` | No | `null` |

Tool error detection strategy: `"none"`, `"regex"`, or `"llm"`.

#### `fsm.detect_tool_error_regex_pattern`

| Type | Required | Default |
|------|----------|---------|
| `string` or `null` | No | `null` |

Regex pattern to use when `detect_tool_errors` is set to `"regex"`.

#### `fsm.detect_tool_error_max_result_length`

| Type | Required | Default |
|------|----------|---------|
| `integer` or `null` | No | `null` |

Maximum tool result length to consider for error detection.

#### `fsm.strict_tool_result_parsing`

| Type | Required | Default |
|------|----------|---------|
| `boolean` or `null` | No | `null` |

Enable strict parsing of tool results.

---

## Prompt Overrides (`prompt`)

Per-LLM prompt configuration. Each sub-object corresponds to a different LLM in the pipeline.

Top-level `flavor` and `version` fields are **broadcast** to every LLM prompt sub-config. Per-LLM overrides (e.g. `pllm`, `rllm`) are applied afterwards and take precedence.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt flavor (broadcast to all LLMs) |
| `version` | `string` | `null` | Prompt version (broadcast to all LLMs) |

### `prompt.pllm`

Planning LLM prompt overrides:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt flavor |
| `version` | `string` | `null` | Prompt version |
| `debug_info_level` | `string` | `"normal"` | Debug info level: `"minimal"`, `"normal"`, `"extra"` |
| `clarify_ambiguous_queries` | `boolean` | `null` | Allow PLLM to ask clarifying questions |
| `context_var_visibility` | `string` | `null` | Context variable visibility: `"none"`, `"basic-notext"`, `"basic-executable"`, `"all-executable"`, `"all"` |
| `query_inline_roles` | `array[string]` | `null` | Message roles to inline in query: `"assistant"`, `"tool"`, `"developer"`, `"system"` |
| `query_role_name_overrides` | `object` | `null` | Map of message role name overrides |
| `query_include_tool_calls` | `boolean` | `null` | Include tool calls in query |
| `query_include_tool_args` | `boolean` | `null` | Include tool arguments in query |
| `query_include_tool_results` | `boolean` | `null` | Include tool results in query |

### `prompt.rllm`

Response LLM prompt overrides:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt flavor |
| `version` | `string` | `null` | Prompt version |
| `debug_info_level` | `string` | `null` | Debug info level |

### `prompt.tllm`

Tool-formulating LLM prompt overrides:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt flavor |
| `version` | `string` | `null` | Prompt version |
| `add_tool_description` | `boolean` | `null` | Add tool description to prompt |
| `add_tool_input_schema` | `boolean` | `null` | Add tool input schema to prompt |

### Other LLM Prompts

`prompt.grllm`, `prompt.qllm`, `prompt.tagllm`, `prompt.policy_llm`, `prompt.error_detector_llm` all support:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt flavor |
| `version` | `string` | `null` | Prompt version |

---

## Response Format Overrides (`response_format`)

#### `response_format.strip_response_content`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Strip the response content. This overrides other inclusion settings.

#### `response_format.include_program`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Include the final program in the response.

#### `response_format.include_policy_check_history`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Include the policy check history in the response.

#### `response_format.include_namespace_snapshot`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Include the namespace snapshot in the response.
