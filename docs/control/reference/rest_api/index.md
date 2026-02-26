# REST API

Sequrity Control API (`https://api.sequrity.ai/control`) provides the following RESTful endpoints.

:white_check_mark: = Supported, :test_tube: = Experimental, :construction: = Coming Soon

## Endpoints

### Chat Completions

| URL | Status | Description |
|-----|--------| ------------|
| `POST /chat/v1/chat/completions` | :white_check_mark: | OpenAI-compatible chat completions (default: [OpenRouter](https://openrouter.ai/)) |
| `POST /chat/openai/v1/chat/completions` | :white_check_mark: | Chat completions with [OpenAI](https://openai.com/) |
| `POST /chat/openrouter/v1/chat/completions` | :white_check_mark: | Chat completions with [OpenRouter](https://openrouter.ai/) |
| `POST /chat/sequrity_azure/v1/chat/completions` | :white_check_mark: | Chat completions with Sequrity Azure |

### Anthropic Messages

| URL | Status | Description |
|-----|--------| ------------|
| `POST /chat/v1/messages` | :white_check_mark: | Anthropic-compatible Messages API (default provider) |
| `POST /chat/anthropic/v1/messages` | :white_check_mark: | Messages API with [Anthropic](https://anthropic.com/) |

### Code Completions

| URL | Status | Description |
|-----|--------| ------------|
| `POST /code/v1/chat/completions` | :white_check_mark: | Code-oriented chat completions (default: [OpenRouter](https://openrouter.ai/)) |
| `POST /code/openai/v1/chat/completions` | :white_check_mark: | Code-oriented chat completions with [OpenAI](https://openai.com/) |
| `POST /code/openrouter/v1/chat/completions` | :white_check_mark: | Code-oriented chat completions with [OpenRouter](https://openrouter.ai/) |
| `POST /code/sequrity_azure/v1/chat/completions` | :white_check_mark: | Code-oriented chat completions with Sequrity Azure |
| `POST /code/v1/messages` | :white_check_mark: | Code-oriented Anthropic Messages (default provider) |
| `POST /code/anthropic/v1/messages` | :white_check_mark: | Code-oriented Messages with Anthropic |
| `POST /code/v1/responses` | :white_check_mark: | Code-oriented Responses API (default: [OpenAI](https://openai.com/)) |
| `POST /code/openai/v1/responses` | :white_check_mark: | Code-oriented Responses with [OpenAI](https://openai.com/) |
| `POST /code/sequrity_azure/v1/responses` | :white_check_mark: | Code-oriented Responses with Sequrity Azure |

### Responses

| URL | Status | Description |
|-----|--------| ------------|
| `POST /chat/v1/responses` | :white_check_mark: | OpenAI-compatible Responses API (default provider) |
| `POST /chat/openai/v1/responses` | :white_check_mark: | Responses API with [OpenAI](https://openai.com/) |
| `POST /chat/sequrity_azure/v1/responses` | :white_check_mark: | Responses API with Sequrity Azure |

### LangGraph

| URL | Status | Description |
|-----|--------| ------------|
| `POST /lang-graph/v1/chat/completions` | :white_check_mark: | Chat completions for [LangGraphExecutor](../sequrity_client/langgraph.md) (default: [OpenRouter](https://openrouter.ai/)) |
| `POST /lang-graph/openai/v1/chat/completions` | :white_check_mark: | LangGraph chat completions with [OpenAI](https://openai.com/) |
| `POST /lang-graph/openrouter/v1/chat/completions` | :white_check_mark: | LangGraph chat completions with [OpenRouter](https://openrouter.ai/) |
| `POST /lang-graph/sequrity_azure/v1/chat/completions` | :white_check_mark: | LangGraph chat completions with Sequrity Azure |
| `POST /lang-graph/anthropic/v1/messages` | :white_check_mark: | LangGraph Messages with Anthropic |

### Policy Generation

| URL | Status | Description |
|-----|--------| ------------|
| `POST /policy-gen/v1/generate` | :white_check_mark: | Generate security policies (default: [OpenRouter](https://openrouter.ai/)) |
| `POST /policy-gen/openai/v1/generate` | :white_check_mark: | Policy generation with [OpenAI](https://openai.com/) |
| `POST /policy-gen/openrouter/v1/generate` | :white_check_mark: | Policy generation with [OpenRouter](https://openrouter.ai/) |
| `POST /policy-gen/anthropic/v1/generate` | :white_check_mark: | Policy generation with [Anthropic](https://anthropic.com/) |
| `POST /policy-gen/sequrity_azure/v1/generate` | :white_check_mark: | Policy generation with Sequrity Azure |

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
| `endpoint_type` | The type of endpoint | `chat`, `code`, `agent`, `lang-graph`, `policy-gen` |
| `service_provider` | Optional LLM service provider | `openai`, `openrouter`, `anthropic`, `sequrity_azure` |
| `version` | API version | `v1` |
| `api_suffix` | API-specific suffix | `chat/completions`, `messages`, `responses`, `generate` |

When `service_provider` is omitted, the default provider is used.

## Documentation

- **[Service Providers](../../../general/rest_api/service_provider.md)** - Available LLM service providers
- **[Chat Completion](chat_completion.md)** - OpenAI-compatible Chat Completions API reference
- **[Responses](responses.md)** - OpenAI-compatible Responses API reference
- **[Messages](messages.md)** - Anthropic-compatible Messages API reference

### Custom Headers

- **[X-Api-Key and X-Session-ID](headers/api_key_session_id.md)** - Authentication and session management
- **[X-Features](headers/security_features.md)** - Enable security features like toxicity filtering and PII redaction
- **[X-Policy](headers/security_policy.md)** - Define SQRT policies for tool access control
- **[X-Config](headers/security_config.md)** - Fine-grained security configuration
