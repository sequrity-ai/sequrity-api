# X-Security-Policy

The `X-Security-Policy` header is a JSON string that defines security policies and policy execution behavior.

This header is **required** when using Headers-Only Mode (must be provided together with `X-Security-Features`).

## Data Structure

```json
{
  "language": "sqrt",
  "codes": "",
  "auto_gen": false,
  "fail_fast": true,
  "internal_policy_preset": {
    "default_allow": true,
    "default_allow_enforcement_level": "soft",
    "enable_non_executable_memory": true,
    "enable_llm_blocked_tag": true,
    "branching_meta_policy": {
      "mode": "deny",
      "producers": [],
      "tags": [],
      "consumers": []
    }
  }
}
```

## Fields

### `language`

| Type | Required | Default |
|------|----------|---------|
| `string` | Yes | - |

The policy language to use. Supported values:

- `sqrt`: SQRT policy code
- `sqrt-lite`: Simplified SQRT policy code
- `cedar`: Cedar policy language

### `codes`

| Type | Required | Default |
|------|----------|---------|
| `string` or `list[string]` | Yes | - |

The policy code as a string or a list of strings. Can be empty (`""` or `[]`) for no custom policies.

### `auto_gen`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

When enabled, security policies are auto-generated based on the user query. The `codes` field can contain natural language instructions when this is enabled.

### `fail_fast`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Stop execution on the first policy violation. **Only available for sqrt languages** (`sqrt`, `sqrt-lite`). Not available for `cedar`.

### `internal_policy_preset`

| Type | Required | Default |
|------|----------|---------|
| `object` | No | See below |

Configuration for internal policies.

#### `internal_policy_preset.default_allow`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

The default action when no policy rules match a tool call. When `true`, tool calls are allowed by default; when `false`, tool calls are denied by default.

#### `internal_policy_preset.default_allow_enforcement_level`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `soft` |

The enforcement level for the default allow/deny policy.

#### `internal_policy_preset.enable_non_executable_memory`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | **Automatically set** |

Enable non-executable memory protection for tool result tags.

**Note:** This value is **automatically determined by the policy language** and any user-provided value will be ignored:

- `true` for sqrt languages (`sqrt`, `sqrt-lite`)
- `false` for `cedar`

#### `internal_policy_preset.enable_llm_blocked_tag`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

When enabled, QLLM inputs tagged with `__llm_blocked` tag will be blocked from being sent to the LLM.

#### `internal_policy_preset.branching_meta_policy`

| Type | Required | Default |
|------|----------|---------|
| `object` | No | See below |

Control flow policy for branching operations.

##### `branching_meta_policy.mode`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"deny"` |

The mode for the branching meta policy:

- `"allow"`: Whitelist mode - only allow specified producers/tags/consumers
- `"deny"`: Blacklist mode - deny specified producers/tags/consumers

##### `branching_meta_policy.producers`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `[]` |

List of producer names to allow (in `allow` mode) or deny (in `deny` mode) for control flow relaxer.

##### `branching_meta_policy.tags`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `[]` |

List of tags to allow (in `allow` mode) or deny (in `deny` mode) for control flow relaxer.

##### `branching_meta_policy.consumers`

| Type | Required | Default |
|------|----------|---------|
| `array[string]` | No | `[]` |

List of consumer names to allow (in `allow` mode) or deny (in `deny` mode) for control flow relaxer.
