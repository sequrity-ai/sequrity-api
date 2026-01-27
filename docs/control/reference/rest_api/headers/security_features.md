# X-Security-Features

The `X-Security-Features` header is a JSON array that defines enabled security features and their configurations.

This header is **required** when using Headers-Only Mode (must be provided together with `X-Security-Policy`).

## Data Structure

```json
[
  {
    "feature_name": "Dual LLM",
    "config_json": "{\"mode\": \"standard\"}"
  },
  {
    "feature_name": "Toxicity Filter",
    "config_json": "{\"enabled\": false, \"mode\": \"normal\"}"
  },
  {
    "feature_name": "PII Redaction",
    "config_json": "{\"enabled\": false, \"threshold\": 0.5}"
  },
  {
    "feature_name": "Healthcare Topic Guardrail",
    "config_json": "{\"enabled\": false, \"mode\": \"strict\"}"
  },
  {
    "feature_name": "Finance Topic Guardrail",
    "config_json": "{\"enabled\": false, \"threshold\": 0.3}"
  },
  {
    "feature_name": "Legal Topic Guardrail",
    "config_json": "{\"enabled\": false, \"tag_name\": \"legal_content\"}"
  },
  {
    "feature_name": "URL Blocker",
    "config_json": "{\"enabled\": false}"
  },
  {
    "feature_name": "Long Program Support",
    "config_json": "{\"mode\": \"mid\"}"
  }
]
```

## Feature Entry Fields

Each entry in the array has the following structure:

### `feature_name`

| Type | Required | Default |
|------|----------|---------|
| `string` | Yes | - |

The display name of the feature to enable. See [Available Features](#available-features) for valid values.

### `config_json`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `null` |

A JSON string containing feature-specific configuration options. The structure depends on the feature type.

---

## Available Features

### Agent Mode Features

Choose one of the following agent modes (mutually exclusive):

#### Single LLM

- **Feature Name:** `"Single LLM"`
- **Description:** Single-model agent mode. The same LLM handles both planning and execution.
- **Config Options:** None

#### Dual LLM

- **Feature Name:** `"Dual LLM"`
- **Description:** Dual-model agent mode with separate planning and execution LLMs.
- **Config Options:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `string` | `"standard"` | Agent mode: `"standard"`, `"strict"`, or `"custom"` |

---

### Tagger Features

Taggers are LLM-based content detection features that analyze tool call inputs and outputs.

**Common Tagger Config Options:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `boolean` | `false` | Enable the tagger |
| `threshold` | `float` | `0.5` | Detection threshold (0.0 - 1.0) |
| `mode` | `string` | `null` | Preset mode: `"normal"` (threshold 0.7) or `"strict"` (threshold 0.3) |
| `tag_name` | `string` | `null` | Override the default tag name |

#### Toxicity Filter

- **Feature Name:** `"Toxicity Filter"`
- **Description:** Detect toxic, harmful, or abusive content in tool call inputs and outputs.

#### PII Redaction

- **Feature Name:** `"PII Redaction"`
- **Description:** Detect and redact personally identifiable information (names, emails, phone numbers, etc.).

#### Healthcare Topic Guardrail

- **Feature Name:** `"Healthcare Topic Guardrail"`
- **Description:** Detect healthcare-related content that may require professional medical advice.

#### Finance Topic Guardrail

- **Feature Name:** `"Finance Topic Guardrail"`
- **Description:** Detect finance-related content that may require professional financial advice.

#### Legal Topic Guardrail

- **Feature Name:** `"Legal Topic Guardrail"`
- **Description:** Detect legal-related content that may require professional legal advice.

---

### Constraint Features

Constraints are non-LLM stateless security checks applied to tool calls.

#### URL Blocker

- **Feature Name:** `"URL Blocker"`
- **Description:** Block URL access in tool calls.
- **Config Options:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `boolean` | `false` | Enable the constraint |

---

### Long Program Support

- **Feature Name:** `"Long Program Support"`
- **Description:** Adjust interpreter gas limits for longer program execution.
- **Config Options:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `string` | `"base"` | Gas limit tier: `"base"` (10K gas), `"mid"` (100K gas), or `"long"` (1M gas) |
