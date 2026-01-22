# Chat Completion REST API Reference

## Overview

The chat completion endpoint supports two modes of operation:

- **Headers-Only Mode**: Configure security settings via HTTP headers (both `X-Security-Policy` and `X-Security-Features` required)
- **Bearer Token Only Mode**: Use pre-configured settings from database (neither header provided)

## Required Headers (All Modes)

### Authorization Header

```http
Authorization: Bearer sk-sq-your-api-key
```

Your Sequrity API key for authentication.

### X-Api-Key (Optional)

```http
X-Api-Key: sk-your-openai-key
```

API key for the LLM service provider (OpenAI, OpenRouter, etc.). If not provided, the server's default key will be used.

### X-Session-ID (Optional)

```http
X-Session-ID: uuid-session-id
```

Session identifier for continuing an existing conversation. If not provided, a new session is created. The session ID is returned in the response headers.

---

## Headers-Only Mode

Headers-only mode enables complete control over security configuration through HTTP headers. This mode is activated when **both** `X-Security-Policy` **and** `X-Security-Features` headers are provided.

### X-Security-Policy (Required for Headers-Only Mode)

JSON string defining security policies and policy execution behavior.

**Format:**

```json
{
  "language": "sqrt",
  "codes": "...",
  "auto_gen": false,
  "fail_fast": true,
  "internal_policy_preset": {
      "default_allow": true,
      "enable_non_executable_memory": true,
      "branching_meta_policy": {
          "mode": "deny",
          "producers": [],
          "tags": [],
          "consumers": []
      },
  }
}
```

**Supported Policy Languages:**

- `sqrt-json`: Pre-compiled JSON policy objects
- `sqrt`: SQRT policy code (will be translated)
- `sqrt-lite`: Simplified SQRT policy code
- `cedar`: Cedar policy language

**Fields:**

- `language` (string, required): Policy language - `"sqrt-json"`, `"sqrt"`, `"sqrt-lite"`, or `"cedar"`
- `codes` (string | list[string], required): Policy code as JSON string or code string (can be empty)
- `fail_fast` (boolean, optional, default: `true`): Stop on first policy violation if true. **Only available for sqrt languages** (sqrt-json, sqrt, sqrt-lite). Not available for cedar.
- `auto_gen` (boolean, optional, default: `false`): Auto-generate security policies based on user query. Available for all languages.
- `internal_policy_preset` (object, optional): Internal policy configuration
  - `default_allow` (boolean, optional, default: `true`): Default policy when no rules match
  - `enable_non_executable_memory` (boolean, **automatically set based on language** - `true` for sqrt languages, `false` for cedar): Enable non-executable memory protection. **Note:** This value is automatically determined by the policy language and any user-provided value will be ignored.
  - `branching_meta_policy` (object, optional): Control flow policy for branching operations
    - `mode` (string, default: `"deny"`): `"allow"` for whitelist, `"deny"` for blacklist
    - `producers` (array of strings, default: `[]`): Producer names to allow/deny
    - `tags` (array of strings, default: `[]`): Tags to allow/deny
    - `consumers` (array of strings, default: `[]`): Consumer names to allow/deny

### X-Security-Features (Required for Headers-Only Mode)

JSON array defining enabled security features. Must be provided together with `X-Security-Policy`.

**Format:**

```json
[
  {
    "feature_name": "Dual LLM",
    "config_json": "{\"mode\": \"standard\"}"
  },
  {
    "feature_name": "Toxicity Filter",
    "config_json": "{\"threshold\": 0.5, \"enabled\": true, \"mode\": \"normal\"}"
  }
]
```

**Available Features:**

1. **Agent Mode** (choose one):
   - `"Single LLM"`: Single-model agent mode
   - `"Dual LLM"`: Dual-model agent mode (planning + execution)
     - `mode`: `"standard"` (default) or `"strict"`

2. **Taggers** (LLM-based content detection):
   - `"Toxicity Filter"`: Detect toxic content
   - `"PII Redaction"`: Detect and redact personally identifiable information
   - `"Healthcare Topic Guardrail"`: Healthcare content detection
   - `"Finance Topic Guardrail"`: Finance content detection
   - `"Legal Topic Guardrail"`: Legal content detection

   **Tagger Config Options:**
   - `threshold` (float, 0.0-1.0): Detection threshold (default: 0.5)
   - `enabled` (boolean): Enable the tagger
   - `mode` (string): `"normal"` (threshold 0.7) or `"strict"` (threshold 0.3)
   - `tag_name` (string, optional): Override default tag name

3. **Constraints** (Non-LLM security checks):
   - `"URL Blocker"`: Block URL access in tool calls

   **Constraint Config Options:**
   - `enabled` (boolean): Enable the constraint
   - `mode` (string, optional): Constraint mode
   - `check_name` (string, optional): Override default check name

4. **Long Program Support**:
   - `"Long Program Support"`: Adjust interpreter gas limits

   **Config Options:**
   - `mode`: `"base"` (10K gas, free), `"mid"` (100K gas), or `"long"` (1M gas)

### X-Security-Config (Optional)

JSON object with additional product configuration settings. All fields are optional and have sensible defaults.

**Format:**

```json
{
  "max_pllm_attempts": 4,
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
  "disable_rllm": false,
  "reduced_grammar_for_rllm_review": true,
  "rllm_confidence_score_threshold": null,
  "pllm_debug_info_level": "normal",
  "max_n_turns": 1,
  "enable_multi_step_planning": false,
  "prune_failed_steps": true,
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

**Available Configuration Fields:**

**Planning & Execution:**

- `max_pllm_attempts` (int, ≥1, default: `4`): Maximum number of PLLM attempts before giving up
- `max_tool_calls_per_attempt` (int, ≥1, default: `200`): Maximum number of tool calls allowed per PLLM attempt. Set to null for no limit.
- `clear_history_every_n_attempts` (int, ≥1, optional, default: `null`): If set, clears tool call history every n PLLM attempts to save tokens
- `retry_on_policy_violation` (boolean, default: `false`): Retry PLLM attempts when a policy violation is detected
- `max_n_turns` (int, ≥1, optional, default: `1`): Maximum conversation turns. Set to null for unlimited turns.
- `enable_multi_step_planning` (boolean, default: `false`): Enable multi-step planning for complex queries
- `prune_failed_steps` (boolean, default: `true`): Prune failed PLLM steps from session history to save tokens
- `show_pllm_secure_var_values` (string, default: `"none"`): Control which secure variable values are shown to PLLM in prompts
  - `"none"`: Do not show any secure variable values
  - `"basic-notext"`: Show values of basic types (bool, int, float, list, tuple) but not strings
  - `"basic-executable"`: Show values of basic types (including strings) marked as executable memory
  - `"all-executable"`: Show all variables marked as executable memory
  - Note: `"basic-executable"` and `"all-executable"` require `enable_non_executable_memory` to be `true` in internal policy preset

**Message Processing:**

- `merge_system_messages` (boolean, default: `true`): Merge multiple system messages into one before sending to PLLM
- `convert_system_to_developer_messages` (boolean, default: `false`): Convert system messages to developer messages in the user query
- `include_other_roles_in_user_query` (list[string], default: `["assistant"]`): Roles to include in user query besides 'user'. Valid values: `"assistant"`, `"tool"`
- `restate_user_query_before_planning` (boolean, default: `false`): Restate the user query before planning to provide clearer context

**Caching:**

- `cache_tool_result` (string, default: `"deterministic-only"`): Tool result caching strategy
  - `"none"`: No caching
  - `"all"`: Cache all results
  - `"deterministic-only"`: Cache only deterministic tools
- `force_to_cache` (list[string], default: `[]`): Tool ID regex patterns to always cache regardless of cache_tool_result setting

**Tool Management:**

- `min_num_tools_for_filtering` (int, ≥2, default: `10`): Minimum number of available tools to trigger tool filtering. If fewer tools available, no filtering is performed.
- `enabled_internal_tools` (list[string], default: `["parse_with_ai", "verify_hypothesis"]`): Internal tools to enable. Valid values: `"parse_with_ai"`, `"verify_hypothesis"`

**Review & Validation:**

- `disable_rllm` (boolean, default: `false`): Disable the Response LLM (RLLM) for reviewing final responses
- `reduced_grammar_for_rllm_review` (boolean, default: `true`): Use reduced grammar for RLLM review process
- `rllm_confidence_score_threshold` (float, 0.0-1.0, optional, default: `null`): Threshold for accepting RLLM review confidence scores
- `reduced_grammar_version` (string, default: `"v2"`): Version of reduced grammar to use - `"v1"` or `"v2"`

**Session Management:**

- `clear_session_meta` (string, default: `"never"`): When to clear session metadata
  - `"never"`: Never clear
  - `"every_attempt"`: Clear at the beginning of each PLLM attempt
  - `"every_turn"`: Clear at the beginning of each turn

**Debug & Output:**

- `pllm_debug_info_level` (string, default: `"normal"`): Debug info level provided to PLLM - `"minimal"`, `"normal"`, or `"extra"`
- `pllm_can_ask_for_clarification` (boolean, default: `false`): Allow PLLM to ask clarifying questions when user query is ambiguous

**Response Format:**

- `response_format` (object, optional): Response format configuration
  - `strip_response_content` (boolean, default: `false`): Strip the response content. This overrides other inclusion settings.
  - `include_program` (boolean, default: `false`): Include the final program in the response
  - `include_policy_check_history` (boolean, default: `false`): Include the policy check history in the response
  - `include_namespace_snapshot` (boolean, default: `false`): Include the namespace screenshot in the response
---

## Endpoint URLs

The API provides two endpoint patterns:

### 1. Default Endpoint (OpenRouter)

```http
POST /v1/chat/completions
```

Uses OpenRouter as the default LLM service provider.

### 2. Provider-Specific Endpoint

```http
POST /{service_provider}/v1/chat/completions
```

Specify a particular LLM service provider. Supported providers:

- `openai` - OpenAI API
- `openrouter` - OpenRouter API
- `azure_credits` - Azure Credits API

**Example:**

```http
POST /openai/v1/chat/completions
```

---

## Mode Selection Logic

The endpoint automatically determines the mode based on provided headers:

- **Headers-Only Mode**: When **both** `X-Security-Policy` **and** `X-Security-Features` are provided
- **Bearer Token Only Mode**: When **neither** `X-Security-Policy` **nor** `X-Security-Features` is provided (uses database configuration)
- **Error**: When only one of `X-Security-Policy` or `X-Security-Features` is provided (both required for headers-only mode)

**Key Points:**

- In Headers-Only Mode, all security configuration is provided via headers
- In Bearer Token Only Mode, configuration is retrieved from the database using your API key
- Session continuations (with `X-Session-ID`) use the existing session's configuration regardless of mode
