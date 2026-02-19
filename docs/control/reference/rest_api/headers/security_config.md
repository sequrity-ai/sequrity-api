# X-Config

The `X-Config` header is a JSON object that provides additional product configuration settings.

This header is **optional** and can be used in Headers-Only Mode to fine-tune session behavior.

## Data Structure

```json
{
  "fsm": {
    "min_num_tools_for_filtering": 10,
    "clear_session_meta": "never",
    "max_n_turns": null,
    "allow_history_mismatch": null,
    "clear_history_every_n_attempts": null,
    "disable_rllm": true,
    "enable_multistep_planning": null,
    "enabled_internal_tools": null,
    "prune_failed_steps": false,
    "force_to_cache": [],
    "max_pllm_steps": null,
    "max_pllm_failed_steps": null,
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
    "pllm": {
      "flavor": null,
      "version": null,
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
      "flavor": null,
      "version": null,
      "debug_info_level": null
    },
    "tllm": {
      "flavor": null,
      "version": null,
      "add_tool_description": null,
      "add_tool_input_schema": null
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
- **`response_format`**: Response format configuration for dual-LLM sessions

All fields are optional and have sensible defaults.

---

## FSM Overrides (`fsm`)

### Shared Fields (Single-LLM & Dual-LLM)

#### `fsm.min_num_tools_for_filtering`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `10` | >= 2 |

Minimum number of registered tools to enable tool-filtering LLM step. Set to `null` to disable.

#### `fsm.clear_session_meta`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"never"` |

When to clear session meta information:

- `"never"`: Never clear
- `"every_attempt"`: Clear at the beginning of each PLLM attempt
- `"every_turn"`: Clear at the beginning of each turn

#### `fsm.max_n_turns`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | endpoint-dependent | >= 1 |

Maximum number of turns allowed in the session. If `null`, unlimited turns are allowed. When not set, the server applies a default based on the endpoint type.

### Dual-LLM Only Fields

#### `fsm.allow_history_mismatch`

| Type | Required | Default |
|------|----------|---------|
| `boolean` or `null` | No | `null` |

Controls behaviour when incoming messages diverge from stored history in stateless mode. When `true`, the server silently truncates its stored history to the last consistent point and accepts the caller's version. When `false`, the server rejects the request with an error if a mismatch is detected.

#### `fsm.clear_history_every_n_attempts`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `null` | >= 1 |

Single-step mode only. Clear all failed step history every N attempts to save tokens.

#### `fsm.disable_rllm`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Whether to skip the response LLM (RLLM) review step.

#### `fsm.enable_multistep_planning`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

When `false` (single-step), each attempt solves independently. When `true` (multi-step), each step builds on previous.

#### `fsm.enabled_internal_tools`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | endpoint-dependent |

List of internal tool IDs available to planning LLM. Valid values: `"parse_with_ai"`, `"verify_hypothesis"`, `"set_policy"`, `"complete_turn"`. When not set, the server applies a default based on the endpoint type.

#### `fsm.prune_failed_steps`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Multi-step mode only. Remove failed steps from history after turn completes.

#### `fsm.force_to_cache`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `[]` |

List of tool ID regex patterns to always cache their results regardless of the cache_tool_result setting.

#### `fsm.max_pllm_steps`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `null` | >= 1 |

Maximum number of steps allowed per turn.

#### `fsm.max_pllm_failed_steps`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `null` | >= 1 |

Maximum number of failed steps allowed per turn.

#### `fsm.max_tool_calls_per_step`

| Type | Required | Default | Constraints |
|------|----------|---------|-------------|
| `integer` or `null` | No | `null` | >= 1 |

Maximum number of tool calls allowed per PLLM attempt. If `null`, no limit is enforced.

#### `fsm.reduced_grammar_for_rllm_review`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Whether to paraphrase RLLM output via reduced grammar before feeding back to planning LLM.

#### `fsm.retry_on_policy_violation`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

When `true`, allow planning LLM to retry after policy violation.

#### `fsm.wrap_tool_result`

| Type | Required | Default |
|------|----------|---------|
| `boolean` or `null` | No | `null` |

Whether to wrap tool results in Ok/Err types.

#### `fsm.detect_tool_errors`

| Type | Required | Default |
|------|----------|---------|
| `string` or `null` | No | `null` |

Whether and how to detect errors in tool results:

- `"none"`: Do not detect tool result errors
- `"regex"`: Use regex patterns to detect common error messages in tool results
- `"llm"`: Use an LLM to analyze tool results and detect potential errors

#### `fsm.detect_tool_error_regex_pattern`

| Type | Required | Default |
|------|----------|---------|
| `string` or `null` | No | `null` |

The regex pattern to use for detecting error messages in tool results when `detect_tool_errors` is set to `"regex"`.

#### `fsm.detect_tool_error_max_result_length`

| Type | Required | Default |
|------|----------|---------|
| `integer` or `null` | No | `null` |

The maximum length of tool result to consider for error detection. Longer results will be truncated. If `null`, no limit is enforced.

#### `fsm.strict_tool_result_parsing`

| Type | Required | Default |
|------|----------|---------|
| `boolean` or `null` | No | `null` |

If `true`, only parse external tool results as JSON when the tool declares an output_schema. When `false`, always attempt `json.loads` on tool results.

---

## Prompt Overrides (`prompt`)

Per-LLM prompt configuration. Each sub-object corresponds to a different LLM in the pipeline.

### `prompt.pllm`

Planning LLM prompt overrides:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt template variant to use (e.g., `"universal"`). |
| `version` | `string` | `null` | Prompt template version. Combined with flavor to load template. |
| `debug_info_level` | `string` | `"normal"` | Level of detail for debug/execution information in planning LLM prompt: `"minimal"`, `"normal"`, `"extra"`. |
| `clarify_ambiguous_queries` | `boolean` | `null` | Whether planning LLM is allowed to ask for clarification on ambiguous queries. |
| `context_var_visibility` | `string` | `null` | The visibility level of context variables in the PLLM prompts: `"none"`, `"basic-notext"`, `"basic-executable"`, `"all-executable"`, `"all"`. |
| `query_inline_roles` | `array[string]` | `null` | List of roles whose messages will be inlined into the user query: `"assistant"`, `"tool"`, `"developer"`, `"system"`. |
| `query_role_name_overrides` | `object` | `null` | Overrides for message role names in the inlined user query. For example, `{"assistant": "developer"}` will change the role of assistant messages to developer. |
| `query_include_tool_calls` | `boolean` | `null` | Whether to include upstream tool calls in inlined query. |
| `query_include_tool_args` | `boolean` | `null` | Whether to include arguments of upstream tool calls. |
| `query_include_tool_results` | `boolean` | `null` | Whether to include results of upstream tool calls. |

### `prompt.rllm`

Review LLM prompt overrides:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt template variant to use (e.g., `"universal"`). |
| `version` | `string` | `null` | Prompt template version. Combined with flavor to load template. |
| `debug_info_level` | `string` | `null` | Level of detail for debug/execution information in RLLM prompt: `"minimal"`, `"normal"`, `"extra"`. |

### `prompt.tllm`

Tool-formulating LLM prompt overrides:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt template variant to use (e.g., `"universal"`). |
| `version` | `string` | `null` | Prompt template version. Combined with flavor to load template. |
| `add_tool_description` | `boolean` | `null` | Whether to include tool descriptions in tool-filtering prompt. |
| `add_tool_input_schema` | `boolean` | `null` | Whether to include tool input JSON schemas in tool-filtering prompt. |

### Other LLM Prompts

`prompt.grllm`, `prompt.qllm`, `prompt.tagllm`, `prompt.policy_llm`, `prompt.error_detector_llm` all support:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `flavor` | `string` | `null` | Prompt template variant to use (e.g., `"universal"`). |
| `version` | `string` | `null` | Prompt template version. Combined with flavor to load template. |

---

## Response Format Overrides (`response_format`)

#### `response_format.strip_response_content`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

When `true`, returns only essential result value as plain text, stripping all metadata.

#### `response_format.include_program`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Whether to include the generated program in the response.

#### `response_format.include_policy_check_history`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Whether to include policy check results even when there are no violations.

#### `response_format.include_namespace_snapshot`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

Whether to include snapshot of all variables after program execution.
