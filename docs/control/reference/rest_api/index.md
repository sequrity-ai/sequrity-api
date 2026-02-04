# REST API

Sequrity Control API (`https://api.sequrity.ai/control`) provides the following RESTful endpoints.

:white_check_mark: = Supported, :test_tube: = Experimental, :construction: = Coming Soon

## Endpoints

| URL | Status | Description |
|-----|-------------| -------------|
| `POST /v1/chat/completions` | :white_check_mark: | Chat completion API with OpenRouter as service provider  |
| `POST /{service_provider}/v1/chat/completions` | :white_check_mark: | Chat completion API with specified [service provider](../../../general/rest_api/service_provider.md) |
| `POST /vscode/{service_provider}/v1/chat/completions` | :test_tube: | Chat completion API for VSCode |
| `POST /lang-graph/{service_provider}/v1/chat/completions` | :test_tube: | Chat completion API for [LangGraphExecutor](../sequrity_client/langgraph.md) |
| `POST /v1/generate_policy` | :test_tube: | Generating security policies |
| `POST /control/v1/responses` | :test_tube: | Responses API with OpenAI as service provider |

## Documentation

- **[Service Providers](../../../general/rest_api/service_provider.md)** - Available LLM service providers
- **[Chat Completion](chat_completion.md)** - Chat completion API reference

### Custom Headers

- **[X-Api-Key and X-Session-Id](headers/api_key_session_id.md)** - Authentication and session management
- **[X-Security-Features](headers/security_features.md)** - Enable security features like toxicity filtering and PII redaction
- **[X-Security-Policy](headers/security_policy.md)** - Define SQRT policies for tool access control
- **[X-Security-Config](headers/security_config.md)** - Fine-grained security configuration