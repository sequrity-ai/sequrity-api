# X-Features

The `X-Features` header is a JSON object that defines the agent architecture and enabled security features.

This header is **required** when using Headers-Only Mode (must be provided together with `X-Policy`).

## Data Structure

```json
{
  "agent_arch": "dual-llm",
  "content_classifiers": [
    {"name": "toxicity_filter", "threshold": 0.5, "mode": "normal"},
    {"name": "pii_redaction", "threshold": 0.5},
    {"name": "healthcare_topic_guardrail", "threshold": 0.5},
    {"name": "finance_topic_guardrail", "threshold": 0.5}
  ],
  "content_blockers": [
    {"name": "url_blocker"},
    {"name": "file_blocker"}
  ]
}
```

## Top-Level Fields

### `agent_arch`

| Type | Required | Default |
|------|----------|---------|
| `string` | No | `null` |

The agent architecture to use. Valid values:

- `"single-llm"`: Single-model agent mode. The same LLM handles both planning and execution.
- `"dual-llm"`: Dual-model agent mode with separate planning and execution LLMs.

### `content_classifiers`

| Type | Required | Default |
|------|----------|---------|
| `array[object]` | No | `null` |

LLM-based content classifiers that analyze tool call arguments (pre-execution) and results (post-execution) to detect sensitive content (e.g., PII, toxicity). Each classifier has the following fields:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | `string` | Yes | - | Classifier identifier (see below) |
| `threshold` | `float` | No | `0.5` | Threshold for the tagger (0.0 - 1.0) |
| `mode` | `string` | No | `null` | Optional mode that overrides threshold (e.g., `"high sensitivity"`, `"strict"`, `"low sensitivity"`, `"normal"`) |

Available classifiers:

- `"toxicity_filter"`: Detect toxic, harmful, or abusive content in tool call inputs and outputs.
- `"pii_redaction"`: Detect and redact personally identifiable information (names, emails, phone numbers, etc.).
- `"healthcare_topic_guardrail"`: Detect healthcare-related content that may require professional medical advice.
- `"finance_topic_guardrail"`: Detect finance-related content that may require professional financial advice.

### `content_blockers`

| Type | Required | Default |
|------|----------|---------|
| `array[object]` | No | `null` |

Content blockers that redact or mask sensitive content in tool call arguments (pre-execution) and results (post-execution). Each blocker has the following fields:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | `string` | Yes | - | Blocker identifier: `"url_blocker"` or `"file_blocker"` (see below) |

Available blockers:

- `"url_blocker"`: Block URL access in tool calls.
- `"file_blocker"`: Block file access in tool calls.
