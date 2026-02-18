# X-Api-Key and X-Session-ID Headers

## X-Api-Key (Optional)

```http
X-Api-Key: your-provider-api-key
```

This header is the LLM API key associated with the service provider you picked, e.g., OpenRouter, Anthropic, etc.

- For example, you need to provide your OpenRouter API key in the `X-Api-Key` header
if you post to `https://api.sequrity.ai/control/chat/openrouter/v1/chat/completions`.
- If not provided (non-BYOK), Sequrity uses its own server-managed API key for the provider. Model names are validated against the server's model allow list, and extra charges may apply.


!!! info "Example: Using X-Api-Key with OpenRouter"

    Chat Completions endpoint for Sequrity Control API uses the service provider in the URL path like so:

    ```bash hl_lines="1 2 6 8"
    SERVICE_PROVIDER="openrouter"
    OPENROUTER_API_KEY="your-openrouter-api-key"

    # 💡 SERVICE_PROVIDER in the URL path
    curl -X POST https://api.sequrity.ai/control/chat/${SERVICE_PROVIDER}/v1/chat/completions \
    -H "Authorization: Bearer $SEQURITY_API_KEY" \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: $OPENROUTER_API_KEY" \
    -d '{
        "model": "openai/gpt-5-mini",
        "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
    }'
    ```



## X-Session-ID (Optional)

```http
X-Session-ID: uuid-session-id
```

Session identifier for continuing an existing conversation. The session ID is returned in the response headers and is encoded into tool call IDs of assistant messages.

- If Session-ID is not provided via the `X-Session-ID` header or no tool result messages in the request messages, a new session is created.
- Otherwise, the conversation history associated with that session ID like previous PLLM plans is used to maintain context.

Most of the time, you don't need to manually manage session IDs.
Refer to the [Session ID in Sequrity Control API](../../../learn/session_id.md) for more details.