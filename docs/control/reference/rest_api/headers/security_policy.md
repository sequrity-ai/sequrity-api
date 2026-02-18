# X-Policy

The `X-Policy` header is a JSON object that defines security policies and policy execution behavior.

This header is **required** when using Headers-Only Mode (must be provided together with `X-Features`).

## Data Structure

```json
{
  "mode": "standard",
  "codes": {"code": "", "language": "sqrt"},
  "auto_gen": false,
  "fail_fast": null,
  "presets": {
    "default_allow": true,
    "default_allow_enforcement_level": "soft",
    "enable_non_executable_memory": true,
    "enable_llm_blocked_tag": true,
    "llm_blocked_tag_enforcement_level": "hard",
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

### `mode`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"standard"` |

The security mode. Valid values:

- `"standard"`: Standard security mode
- `"strict"`: Strict security mode with additional constraints
- `"custom"`: Custom security mode for advanced use cases

### `codes`

| Type | Required | Default |
|------|----------|---------|
| `object` | No | `{"code": "", "language": "sqrt"}` |

An object containing the policy code and its language. Fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `code` | `string` | `""` | The policy code. Can be empty for no custom policies. |
| `language` | `string` | `"sqrt"` | The policy language: `"sqrt"` or `"cedar"`. |

### `auto_gen`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `false` |

When enabled, security policies are auto-generated based on the user query. The `codes` field can contain natural language instructions when this is enabled.

### `fail_fast`

| Type | Required | Default |
|------|----------|---------|
| `boolean` or `null` | No | `null` |

Stop execution on the first policy violation.

### `presets`

| Type | Required | Default |
|------|----------|---------|
| `object` | No | See below |

Internal policy presets configuration.

#### `presets.default_allow`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

The default action when no policy rules match a tool call. When `true`, tool calls are allowed by default; when `false`, tool calls are denied by default.

#### `presets.default_allow_enforcement_level`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"soft"` |

The enforcement level for the default allow/deny policy. Valid values: `"hard"`, `"soft"`.

#### `presets.enable_non_executable_memory`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Inject non-executable tag to tool result tags by default.

#### `presets.enable_llm_blocked_tag`

| Type | Required | Default |
|------|----------|---------|
| `boolean` | No | `true` |

Whether to enable hard deny when `__llm_blocked` tag is in args of parse_with_ai.

#### `presets.llm_blocked_tag_enforcement_level`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `"hard"` |

The enforcement level for the LLM blocked tag policy. Valid values: `"hard"`, `"soft"`.

#### `presets.branching_meta_policy`

| Type | Required | Default |
|------|----------|---------|
| `object` | No | See below |

Metadata that are allowed or forbidden in branching.

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
