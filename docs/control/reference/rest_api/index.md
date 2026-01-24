# REST API

Sequrity Control API (`https://api.sequrity.ai/control`) provides the following RESTful endpoints

✅ = Supported, 🧪 = Experimental, 🚧 = Comming Soon

| URL | Status | Description |
|-----|-------------| -------------|
| `POST /v1/chat/completions` | ✅ | Chat completion API with OpenRouter as service provider  |
| `POST /{service_provider}/v1/chat/completions` | ✅ | Chat completion API with specified [service provider](../../../general/rest_api/service_provider.md) |
| `POST /vscode/{service_provider}/v1/chat/completions` | 🧪 | Chat completion API for VSCode |
| `POST /lang-graph/{service_provider}/v1/chat/completions` | 🧪 | Chat completion API for [LangGraphExecutor](../sequrity_client/langgraph.md) |
| `POST /v1/generate_policy` | 🧪 | Generating security policies |
| `POST /control/v1/responses` | 🧪 | Responses API with OpenAI as service provider |