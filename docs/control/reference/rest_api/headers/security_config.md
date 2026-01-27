# X-Security-Config

The `X-Security-Config` header is a JSON object that provides additional product configuration settings.

This header is **optional** and can be used in Headers-Only Mode to fine-tune session behavior.

## Data Structure

```json
{
  "max_pllm_attempts": 1,
  "merge_system_messages": true,
  "convert_system_to_developer_messages": false,
  "include_other_roles_in_user_query": ["assistant"],
  "max_tool_calls_per_attempt": 200,
  "clear_history_every_n_attempts": null,
  "retry_on_policy_violation": false,
  "cache_tool_result": "deterministic-only",
  "force_to_cache": [],
  "min_num_tools_for_filtering": 10,
  "clear_session_meta": "never",
  "disable_rllm": true,
  "reduced_grammar_for_rllm_review": true,
  "rllm_confidence_score_threshold": null,
  "pllm_debug_info_level": "normal",
  "max_n_turns": 5,
  "enable_multi_step_planning": false,
  "prune_failed_steps": false,
  "enabled_internal_tools": ["parse_with_ai", "verify_hypothesis"],
  "restate_user_query_before_planning": false,
  "pllm_can_ask_for_clarification": false,
  "reduced_grammar_version": "v2",
  "show_pllm_secure_var_values": "none",
  "response_format": {
    "strip_response_content": false,
    "include_program": false,
    "include_policy_check_history": false,
    "include_namespace_snapshot": false
  }
}
```

## Fields

All fields are optional and have sensible defaults.

---

### Planning & Execution

#### `max_pllm_attempts`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` | No | `1` | >= 1 |

Maximum number of PLLM attempts before giving up and returning an error.

#### `max_tool_calls_per_attempt`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `200` | >= 1 |

Maximum number of tool calls allowed per PLLM attempt. Set to `null` for no limit.

#### `clear_history_every_n_attempts`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `null` | >= 1 |

If set, clears the tool call history every n PLLM attempts to save token usage.

#### `retry_on_policy_violation`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Retry PLLM attempts when a policy violation is detected.

#### `max_n_turns`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `5` | >= 1 |

Maximum number of conversation turns allowed in the session. Set to `null` for unlimited turns.

#### `enable_multi_step_planning`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Enable multi-step planning for complex user queries.

#### `prune_failed_steps`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Prune failed PLLM steps from session history to save tokens.

#### `show_pllm_secure_var_values`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"none"` |

Control which secure variable values are shown to PLLM in prompts:

- `"none"`: Do not show any secure variable values
- `"basic-notext"`: Show values of basic types (bool, int, float, list, tuple) but not strings
- `"basic-executable"`: Show values of basic types (including strings) marked as executable memory
- `"all-executable"`: Show all variables marked as executable memory

**Note:** `"basic-executable"` and `"all-executable"` require `enable_non_executable_memory` to be `true` in the internal policy preset.

#### `pllm_debug_info_level`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"normal"` |

Debug info level provided to PLLM: `"minimal"`, `"normal"`, or `"extra"`.

#### `pllm_can_ask_for_clarification`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Allow PLLM to ask clarifying questions when the user query is ambiguous.

---

### Message Processing

#### `merge_system_messages`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Merge multiple system messages into one before sending to PLLM.

#### `convert_system_to_developer_messages`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Convert system messages to developer messages in the user query.

#### `include_other_roles_in_user_query`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `["assistant"]` |

Roles to include in the user query besides `"user"`. Valid values: `"assistant"`, `"tool"`.

#### `restate_user_query_before_planning`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Restate the user query before planning to provide clearer context.

---

### Caching

#### `cache_tool_result`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"deterministic-only"` |

Tool result caching strategy:

- `"none"`: No caching
- `"all"`: Cache all tool results
- `"deterministic-only"`: Cache only deterministic tool results

#### `force_to_cache`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `[]` |

List of tool ID regex patterns to always cache regardless of the `cache_tool_result` setting.

---

### Tool Management

#### `min_num_tools_for_filtering`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `10` | >= 2 |

Minimum number of available tools to trigger tool filtering. If fewer tools are available, no filtering is performed.

#### `enabled_internal_tools`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `["parse_with_ai", "verify_hypothesis"]` |

Internal tools to enable. Valid values: `"parse_with_ai"`, `"verify_hypothesis"`.

---

### Review & Validation

#### `disable_rllm`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Disable the Response LLM (RLLM) for reviewing final responses.

#### `reduced_grammar_for_rllm_review`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Use reduced grammar for the RLLM review process.

#### `rllm_confidence_score_threshold`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `float` or `null` | No | `null` | 0.0 - 1.0 |

Threshold for accepting RLLM review confidence scores.

#### `reduced_grammar_version`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"v2"` |

Version of reduced grammar to use for RLLM review: `"v1"` or `"v2"`.

---

### Session Management

#### `clear_session_meta`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"never"` |

When to clear session metadata:

- `"never"`: Never clear
- `"every_attempt"`: Clear at the beginning of each PLLM attempt
- `"every_turn"`: Clear at the beginning of each turn

---


### Response Format

#### `response_format`

| Type | Required | Default |
|------|----------|---------|
| `object` | No | See below |

Configuration for the response format.

##### `response_format.strip_response_content`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Strip the response content. This overrides other inclusion settings.

##### `response_format.include_program`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Include the final program in the response.

##### `response_format.include_policy_check_history`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Include the policy check history in the response.

##### `response_format.include_namespace_snapshot`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Include the namespace screenshot in the response.
