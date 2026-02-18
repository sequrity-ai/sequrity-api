# Service Provider

Some Sequrity API endpoints support multiple LLM service providers. The service provider is part of the endpoint URL between the endpoint type and the API version. For example, the Sequrity Control chat completion endpoint for OpenRouter is:

```
POST https://api.sequrity.ai/control/chat/openrouter/v1/chat/completions
```

When the service provider is omitted from the URL, the default provider is used:

```
POST https://api.sequrity.ai/control/chat/v1/chat/completions
```

## Supported Providers

| Service Provider | Description | Status |
|------------------|-------------| ------|
| `openai` | [OpenAI](https://openai.com/) | :white_check_mark: Supported |
| `openrouter` | [OpenRouter](https://openrouter.ai/) | :white_check_mark: Supported |
| `anthropic` | [Anthropic](https://anthropic.com/) | :white_check_mark: Supported |

!!! note "Anthropic Messages API"

    The Anthropic provider uses the Messages API format (`/messages`) instead of the chat completions format (`/chat/completions`). See the [REST API reference](../../control/reference/rest_api/index.md) for the full list of endpoints.
