# X-Api-Key and X-Session-Id Headers

## X-Api-Key (Optional)

```http
X-Api-Key: your-sequrity-api-key
```

This header is the LLM service API key associated with the service provider you picked.

- For example, you need to provide your OpenRouter API key in the `X-Api-Key` header
if you post to `https://api.sequrity.ai/control/openrouter/v1/chat/completions`.
- If not provided, Sequrity will use its own API key for the service provider with *extra charges*.


!!! info "Service Provider"

    Chat Completions endpoint for Sequrity Control API uses the service provider in the URL path like so:

    ```bash hl_lines="1 2 5 8"
    SERVICE_PROVIDER="openrouter"
    OPENROUTER_API_KEY="your-openrouter-api-key"

    # 💡 SERVICE_PROVIDER in the URL path
    curl -X POST https://api.sequrity.ai/control/${SERVICE_PROVIDER}/v1/chat/completions \
    -H "Authorization: Bearer $SEQURITY_API_KEY" \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: $OPENROUTER_API_KEY" \
    -H 'X-Security-Policy: {"language":"sqrt-lite","codes":""}' \
    -H 'X-Security-Features: [{"feature_name":"Single LLM","config_json":"{\"mode\":\"standard\"}"},{"feature_name":"Long Program Support","config_json":"{\"mode\":\"base\"}"}]' \
    -d '{
        "model": "openai/gpt-5-mini",
        "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
    }'
    ```



## X-Session-ID (Optional)

```http
X-Session-ID: uuid-session-id
```

Session identifier for continuing an existing conversation. The session ID is returned in the response headers.

- If not provided, a new session is created.
- If provided, the conversation history associated with that session ID like previous PLLM plans is used to maintain context.