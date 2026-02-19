# Custom Headers

The Sequrity Control API supports a set of custom HTTP headers for authentication, session management, and configuring security behavior. These headers fall into two categories: standard headers used in all requests, and Headers-Only Mode headers that allow you to define features and policies inline without pre-configuring a project.

## Headers Summary

| Header | Required | Description |
|--------|----------|-------------|
| [`X-Api-Key`](api_key_session_id.md#x-api-key-optional) | No | LLM provider API key (BYOK). If omitted, Sequrity uses its server-managed key. |
| [`X-Session-ID`](api_key_session_id.md#x-session-id-optional) | No | Session identifier for continuing an existing conversation. |
| [`X-Features`](security_features.md) | Required in Headers-Only Mode | JSON object defining the agent architecture and enabled security features (classifiers, blockers). Must be paired with `X-Policy`. |
| [`X-Policy`](security_policy.md) | Required in Headers-Only Mode | JSON object defining security policies and enforcement behavior. Must be paired with `X-Features`. |
| [`X-Config`](security_config.md) | No | JSON object for fine-tuning session execution behavior, prompt overrides, and response format settings. |

