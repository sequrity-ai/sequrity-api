# REST API

Sequrity Control API (`https://api.sequrity.ai/control`) provides the following RESTful endpoints.

:white_check_mark: = Supported, :test_tube: = Experimental, :construction: = Coming Soon

## Endpoints

### Chat Completions

| URL | Status | Description |
|-----|--------| ------------|
| `POST /chat/v1/chat/completions` | :white_check_mark: | OpenAI-compatible chat completions (default provider) |
| `POST /chat/openai/v1/chat/completions` | :white_check_mark: | Chat completions with [OpenAI](https://openai.com/) |
| `POST /chat/openrouter/v1/chat/completions` | :white_check_mark: | Chat completions with [OpenRouter](https://openrouter.ai/) |

### Anthropic Messages

| URL | Status | Description |
|-----|--------| ------------|
| `POST /chat/v1/messages` | :white_check_mark: | Anthropic-compatible Messages API (default provider) |
| `POST /chat/anthropic/v1/messages` | :white_check_mark: | Messages API with [Anthropic](https://anthropic.com/) |

### Code Completions

| URL | Status | Description |
|-----|--------| ------------|
| `POST /code/v1/chat/completions` | :white_check_mark: | Code-oriented chat completions (default provider) |
| `POST /code/{service_provider}/v1/chat/completions` | :white_check_mark: | Code-oriented chat completions with specified [service provider](../../../general/rest_api/service_provider.md) |
| `POST /code/v1/messages` | :white_check_mark: | Code-oriented Anthropic Messages (default provider) |
| `POST /code/anthropic/v1/messages` | :white_check_mark: | Code-oriented Messages with Anthropic |

### LangGraph

| URL | Status | Description |
|-----|--------| ------------|
| `POST /lang-graph/v1/chat/completions` | :white_check_mark: | Chat completions for [LangGraphExecutor](../sequrity_client/langgraph.md) (default provider) |
| `POST /lang-graph/{service_provider}/v1/chat/completions` | :white_check_mark: | LangGraph chat completions with specified [service provider](../../../general/rest_api/service_provider.md) |
| `POST /lang-graph/anthropic/v1/messages` | :white_check_mark: | LangGraph Messages with Anthropic |

### Policy Generation

| URL | Status | Description |
|-----|--------| ------------|
| `POST /policy-gen/v1/generate` | :white_check_mark: | Generate security policies from natural language descriptions |

### Utility

| URL | Status | Description |
|-----|--------| ------------|
| `GET /` | :white_check_mark: | Root endpoint listing all available routes |
| `GET /health` | :white_check_mark: | Health check for load balancers and monitoring |

## URL Pattern

All endpoints follow this URL pattern:

```
https://api.sequrity.ai/control/{endpoint_type}/{service_provider?}/{version}/{api_suffix}
```

| Segment | Description | Examples |
|---------|-------------|---------|
| `endpoint_type` | The type of endpoint | `chat`, `code`, `lang-graph`, `policy-gen` |
| `service_provider` | Optional LLM service provider | `openai`, `openrouter`, `anthropic`, `sequrity_azure` |
| `version` | API version | `v1` |
| `api_suffix` | API-specific suffix | `chat/completions`, `messages`, `generate` |

When `service_provider` is omitted, the default provider is used.

## Documentation

- **[Service Providers](../../../general/rest_api/service_provider.md)** - Available LLM service providers
- **[Chat Completion](chat_completion.md)** - OpenAI-compatible Chat Completions API reference
- **[Messages](messages.md)** - Anthropic-compatible Messages API reference

### Custom Headers

- **[X-Api-Key and X-Session-ID](headers/api_key_session_id.md)** - Authentication and session management
- **[X-Features](headers/security_features.md)** - Enable security features like toxicity filtering and PII redaction
- **[X-Policy](headers/security_policy.md)** - Define SQRT policies for tool access control
- **[X-Config](headers/security_config.md)** - Fine-grained security configuration
