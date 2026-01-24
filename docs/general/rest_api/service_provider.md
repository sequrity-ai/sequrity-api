# Servier Provider

Some Sequrity API endpoints support multiple LLM service providers. The service provider is usually part of the endpoint URL. For example, the Sequrity Control API chat completion endpoint for OpenRouter is:

```
POST https://api.sequrity.ai/control/openrouter/v1/chat/completions
```


| Service Provider | Description | Status |
|------------------|-------------| ------|
| `openrouter` | [OpenRouter](https://openrouter.ai/) | ️✅ Supported |
| `openai` | [OpenAI](https://openai.com/) | ✅ Supported |
| `azurecredits` | [Azure OpenAI](https://azure.microsoft.com/en-gb/products/ai-foundry/models/openai/) | ⚠️ Not yet supported |
