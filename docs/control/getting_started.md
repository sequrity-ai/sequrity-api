# Getting Started with Sequrity Control API

This guide shows you how to send your first chat completion request through the Sequrity Control API.

## Prerequisites

- A Sequrity API key (from your dashboard at [sequrity.ai](https://sequrity.ai/))
- An LLM provider API key (e.g., OpenAI, OpenRouter)

## Installation

=== "Sequrity Client"

    Install the Sequrity Python client:

    ```bash
    pip install sequrity-api
    ```

=== "REST API"

    No installation required. Use any HTTP client (curl, httpx, requests, etc.).

## Sending Your First Message

The simplest way to use the Sequrity Control API is with default settings using Single LLM or Dual LLM mode.

### Single LLM Mode

Single LLM mode passes your request directly to the LLM with optional security taggers and constraints.

=== "Sequrity Client"

    ```python
    from sequrity_api import SequrityClient
    from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader

    # Initialize the client
    client = SequrityClient(api_key="your-sequrity-api-key")

    # Create feature and policy headers
    features = FeaturesHeader.create_single_llm_headers()
    policy = SecurityPolicyHeader.create_default()

    # Send a chat completion request
    response = client.control.create_chat_completion(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini", # model name from your LLM provider
        llm_api_key="your-openrouter-key",
        features=features,
        security_policy=policy,
        service_provider="openrouter",  # or "openai"
    )

    # Print the response
    print(response.choices[0].message.content)
    ```

=== "REST API"

    ```bash
    curl -X POST https://api.sequrity.ai/control/v1/chat/completions \
      -H "Authorization: Bearer your-sequrity-api-key" \
      -H "Content-Type: application/json" \
      -H "X-Api-Key: your-openrouter-key" \
      -H 'X-Security-Policy: {"language":"sqrt-lite","codes":""}' \
      -H 'X-Security-Features: [{"feature_name":"Single LLM","config_json":"{\"mode\":\"standard\"}"},{"feature_name":"Long Program Support","config_json":"{\"mode\":\"base\"}"}]' \
      -d '{
        "model": "openai/gpt-5-mini",
        "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
      }'
    ```

### Dual LLM Mode

Dual LLM mode uses a planning LLM to generate secure execution plans on which security policies and features are enforced. This provides stronger security guarantees for agentic use cases.


=== "Sequrity Client"

    ```python
    from sequrity_api import SequrityClient
    from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader

    # Initialize the client
    client = SequrityClient(api_key="your-sequrity-api-key")

    # Create dual LLM feature headers
    features = FeaturesHeader.create_dual_llm_headers()
    policy = SecurityPolicyHeader.create_default()

    # Send a chat completion request
    response = client.control.create_chat_completion(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini",
        llm_api_key="sk-your-openrouter-key",
        features=features,
        security_policy=policy,
    )

    print(response.choices[0].message.content)
    ```

=== "REST API"

    ```bash
    curl -X POST https://api.sequrity.ai/control/v1/chat/completions \
      -H "Authorization: Bearer your-sequrity-api-key" \
      -H "Content-Type: application/json" \
      -H "X-Api-Key: sk-your-openrouter-key" \
      -H 'X-Security-Policy: {"language":"sqrt-lite","codes":""}' \
      -H 'X-Security-Features: [{"feature_name":"Dual LLM","config_json":"{\"mode\":\"standard\"}"},{"feature_name":"Long Program Support","config_json":"{\"mode\":\"base\"}"}]' \
      -d '{
        "model": "openai/gpt-5-mini",
        "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
      }'
    ```

## Response Format

The response follows the OpenAI Chat Completions format:

=== "Single-LLM Sequrity Client"

    ```python
    ChatCompletionResponse(
        id="gen-1769043728-aRBhZvLVJRJe7IJGnjXO",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ResponseMessage(
                    role="assistant",
                    content="97\n\n97 is prime because it's not divisible by 2, 3, 5, or 7 (the primes ≤ √97 ≈ 9.85).",
                    refusal=None,
                    annotations=None,
                    audio=None,
                    function_call=None,
                    tool_calls=None,
                ),
                logprobs=None,
            )
        ],
        created=1769043728,
        model="openai/gpt-5-mini",
        object="chat.completion",
        usage=CompletionUsage(completion_tokens=105, prompt_tokens=16, total_tokens=121),
        session_id="f9ba994f-f72d-11f0-9a63-e4261df3ef60",
    )
    ```

=== "Single-LLM REST API"

    ```json
    {
    "id": "gen-1769043249-xDdDWhvVTwkwAHCDyBSf",
    "choices": [
        {
        "finish_reason": "stop",
        "index": 0,
        "message": {
            "content": "97\n\n97 is prime because it has no divisors other than 1 and itself (checking primes 2, 3, 5, and 7 — none divide 97).",
            "role": "assistant"
        }
        }
    ],
    "created": 1769043249,
    "model": "openai/gpt-5-mini",
    "object": "chat.completion",
    "usage": {
        "completion_tokens": 108,
        "prompt_tokens": 16,
        "total_tokens": 124
    }
    }
    ```

=== "Dual-LLM Sequrity Client"

    ```python
    ChatCompletionResponse(
        id="7f4f6398-f72d-11f0-b822-0f87f79310f1",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ResponseMessage(
                    role="assistant",
                    content='{"status": "success", "final_return_value": {"value": 97, "meta": {"tags": [], "consumers": ["*"], "producers": []}}}',
                    refusal=None,
                    annotations=None,
                    audio=None,
                    function_call=None,
                    tool_calls=None,
                ),
                logprobs=None,
            )
        ],
        created=1769043533,
        model="openai/gpt-5-mini,openai/gpt-5-mini",
        object="chat.completion",
        usage=CompletionUsage(completion_tokens=304, prompt_tokens=2881, total_tokens=3185),
        session_id="7f4f6398-f72d-11f0-b822-0f87f79310f1",
    )
    ```

=== "Dual-LLM REST API"

    ```json
    {
    "id": "df728048-f72c-11f0-b1e5-0f87f79310f1",
    "choices": [
        {
        "finish_reason": "stop",
        "index": 0,
        "message": {
            "content": "{\"status\": \"success\", \"final_return_value\": {\"value\": 97, \"meta\": {\"tags\": [], \"consumers\": [\"*\"], \"producers\": []}}}",
            "role": "assistant"
        }
        }
    ],
    "created": 1769043264,
    "model": "openai/gpt-5-mini,openai/gpt-5-mini",
    "object": "chat.completion",
    "usage": {
        "completion_tokens": 312,
        "prompt_tokens": 2889,
        "total_tokens": 3201
    }
    }
    ```

The response of dual-llm mode also includes a session ID in the `X-Session-ID` header, which can be used for multi-turn conversations.

## Next Steps

- See more [security features](./reference/features.md) like toxicity filtering and PII redaction
- Explore [security policies](./reference/secure_policies.md) for fine-grained control
- Learn about [advanced configurations](./reference/fine_grained_configs.md)
- See [examples](./examples/example-1.md) for more advanced use cases