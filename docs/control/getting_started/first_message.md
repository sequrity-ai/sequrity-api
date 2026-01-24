# Sending Your First Message with Sequrity Control API

This guide shows you how to send your first chat completion request through the Sequrity Control API.

## Prerequisites

- **Sequrity API Key**: Sign up at [Sequrity](https://sequrity.ai) to get your API key from the dashboard
- **LLM Provider API Key**: This example uses OpenRouter, but you can use any supported provider

??? question "Download Tutorial Scripts"

    - [Sequrity Client version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/first_message/sequrity_client.py)

    - [REST API version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/first_message/rest_api.sh)

## Installation

You can interact with the Sequrity Control API using either the Sequrity Python client or directly via REST API calls.

=== "Sequrity Client"

    Install the Sequrity Python client:

    ```bash
    pip install sequrity-api
    ```

=== "REST API"

    No installation required. Use any HTTP client (curl, httpx, requests, etc.).

## Sending Your First Message

Both Sequrity client and REST API are similar to OpenAI's Chat Completions API, with additional headers for security features and policies.



Sequrity Control API supports two architectures for interacting with LLMs:

- **Single-LLM** is how most existing applications interact with LLMs today, i.e., sending all requests to a single LLM, and letting the LLM handle both instruction and data.
- **Dual-LLM** uses a planning LLM (pllm) to generate execution plans, and a quarantined LLM (qllm) to process data, which provides stronger security guarantees.

??? question "Learn More about single vs dual LLM?"
    See [Single vs Dual LLM](../learn/single-vs-dual-llm.md) for a detailed comparison.

### Single-LLM

#### Request

You can specify Single-LLM by

- using `FeaturesHeader.create_single_llm_headers` (Sequrity client), or
- setting the `X-Security-Features` headers in your request (REST API)

together with your `SecurityPolicyHeader` / security policy headers.

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/getting_started/first_message/sequrity_client.py:13:14,26:45"
    ```

=== "REST API"

    ```bash
    --8<-- "examples/control/getting_started/first_message/rest_api.sh:19:28"
    ```

#### Response

The response of Single-LLM follows the OpenAI Chat Completions format:

=== "Sequrity Client"

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

=== "REST API"

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


??? info "Bearer-Token-only, Headers-mode, and Fine-grained Configurations"
    **Bearer-Token-only vs Headers-mode**: When making requests to the Sequrity Control API, you have two options for specifying security features, policies, and fine-grained configurations: Bearer-Token-only mode and Headers-mode. Refer to [Bearer-Token-only vs Headers-Mode](../reference/rest_api/bearer-token-only-vs-headers-mode.md) for details.

    **Fine-grained Configurations**:
    You can further customize the chat session with fine-grained configurations, such as `max_pllm_attempts`, `cache_tool_results`, etc.
    See [Fine-grained Configurations](../reference/rest_api/headers/security_config.md) for details.


### Dual-LLM

#### Request

You can specify Dual-LLM by

- using `FeaturesHeader.create_dual_llm_headers` (Sequrity client), or
- setting the `X-Security-Features` headers in your request (REST API)

together with your `SecurityPolicyHeader` / security policy headers.

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/getting_started/first_message/sequrity_client.py:56:73"
    ```

=== "REST API"

    ```bash
    --8<-- "examples/control/getting_started/first_message/rest_api.sh:39:48"
    ```

#### Response

The response of Dual-LLM follows the OpenAI Chat Completions format,
except that the response headers include a **session ID** (`X-Session-ID`),
which can be sent back in subsequent request headers for multi-turn conversations.

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

## Next Steps

In the examples above, Dual-LLM seems not very different from Single-LLM.
However, Dual-LLM enables advanced security features when tool calls are involved.
Learn more in [Secure Tool Use with Dual-LLM](./tool_use_dual_llm.md).

More resources explaining Security Features, Security Policies, and Fine-grained Configurations:

- See more [security features](../reference/rest_api/headers/security_features.md) like toxicity filtering and PII redaction
- Explore [security policies](../reference/rest_api/headers/security_policy.md) for fine-grained control
- Learn about [advanced configurations](../reference/rest_api/headers/security_config.md)
- See [examples](../examples/index.md) for more advanced use cases