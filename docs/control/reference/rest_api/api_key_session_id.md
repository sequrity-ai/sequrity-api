# Bearer Token, X-Api-Key, and X-Session-Id Headers

## Bearer Token (Required)

```http
Authorization: Bearer sk-sq-your-api-key
```

Your Sequrity API key for authentication.

## X-Api-Key (Required)

```http
X-Api-Key: sk-sq-your-api-key
```

This header is the LLM service API key associated with the service provider you picked (e.g., OpenAI, OpenRouter, etc.). It is used by Sequrity to forward requests to the underlying LLM service.

### X-Session-ID (Optional)

```http
X-Session-ID: uuid-session-id
```

Session identifier for continuing an existing conversation.
If not provided, a new session is created. The session ID is returned in the response headers.