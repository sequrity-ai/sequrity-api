# Sending Your First Message with Sequrity Control API

This guide shows you how to send your first chat completion request through the [Sequrity Control API][sequrity._client.SequrityClient].

## Prerequisites

- **Sequrity API Key**: Log in to the [Sequrity Dashboard](https://sequrity.ai/dashboard), navigate to **API Keys**, and create a new API key by selecting **Dual LLM** option.
- **LLM Provider API Key**: You can consider Sequrity as a relay service that forwards your requests to LLM service providers, thus you need to offer LLM API keys. This example uses OpenRouter, but you can use any supported provider[^1]

[^1]: See [Supported Providers](../../general/rest_api/service_provider.md) for a list of supported LLM providers in REST API, and [LLM Service Provider Enum](../../general/sequrity_client/service_provider.md) for Sequrity Client.

??? tip "Download Tutorial Scripts"

    - [Sequrity Client version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/first_message/sequrity_client.py)

    - [REST API version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/first_message/rest_api.sh)

## Installation

You can interact with the Sequrity Control API using either the Sequrity Python client or directly via REST API calls.

=== "Sequrity Client"

    Install the Sequrity Python client:

    ```bash
    pip install sequrity
    ```

=== "REST API"

    No installation required. Use any HTTP client (curl, httpx, requests, etc.).

## Sending Your First Message

Both Sequrity client and REST API are compatible with [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat) and [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages). In this example, we use OpenAI Chat Completions API.

### Request

Let's send a simple message asking "What is the largest prime number below 100?"

=== "Sequrity Client"
    ```python
    --8<-- "examples/control/getting_started/first_message/sequrity_client.py:imports_os"
    --8<-- "examples/control/getting_started/first_message/sequrity_client.py:imports_sequrity_client"
    --8<-- "examples/control/getting_started/first_message/sequrity_client.py:api_keys"

    --8<-- "examples/control/getting_started/first_message/sequrity_client.py:first_message"
    --8<-- "examples/control/getting_started/first_message/sequrity_client.py:main"
    --8<-- "examples/control/getting_started/first_message/sequrity_client.py:run_first_message"
    ```

    We create an instance of `SequrityClient` with your Sequrity API key, and send messages using [`chat.create`][sequrity.control.resources.chat.ChatResource.create], specifying the model name on OpenRouter and your OpenRouter API key.

=== "REST API"

    ```bash
    --8<-- "examples/control/getting_started/first_message/rest_api.sh:setup_env_vars"

    --8<-- "examples/control/getting_started/first_message/rest_api.sh:first_message"
    ```

    We use `curl` to send a POST request to the Sequrity Control API's endpoint for OpenRouter, specifying the model name on OpenRouter and your OpenRouter API key in the request body.

### Response

The response follows [the OpenAI Chat Completions format](https://platform.openai.com/docs/api-reference/chat/create).

??? info "Minor Difference from OpenAI Chat Completions API"

    Compared to OpenAI's Chat Completions API, Sequrity Control API adds an extra piece of information to the response, **Session ID**.

    - For Sequrity client, the session ID is available as [`ChatCompletionResponse.session_id`][sequrity.types.chat_completion.response.ChatCompletionResponse.session_id].
    - For REST API, the response has a custom header [`X-Session-ID`](../reference/rest_api/headers/api_key_session_id.md#x-session-id-optional) for REST API.

    The session ID is for maintaining context across multiple interactions in a chat session.

    **However, users do not need to manually handle session IDs in most cases**,
    because Sequrity Control also encodes session ID into tool call ID of ChatCompletion requests, and will parse the session ID from requests with tool results.

    Read more in [Session ID and Multi-turn Sessions](../learn/session_id.md).

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

## Specifying Single/Dual LLM

You may notice we selected Dual LLM when creating the API key in [Prerequisites](#prerequisites).
Sequrity Control API supports two architectures for interacting with LLMs:

- **Single-LLM** is how most existing applications interact with LLMs today, i.e., sending all requests to a single LLM, and letting the LLM handle everything, including
both instruction and data. Sequrity Control adds [*basic security features*](../reference/single_llm_vs_dual_llm_features.md) on top of this architecture.

- **Dual-LLM** uses a planning LLM (pllm) to generate execution plans, and a quarantined LLM (qllm) to process data, which
decouples control flow from data flow, and
provides [*advanced and stronger security guarantees*](../reference/single_llm_vs_dual_llm_features.md).

    ??? question "Learn More about single vs dual LLM?"
        See [Single vs Dual LLM](../learn/single-vs-dual-llm.md) for a detailed comparison.

You can specify Single-LLM or Dual-LLM mode in either of the following two ways:

1. **Select mode when creating API key**

    Log in to the [Sequrity Dashboard](https://sequrity.ai/dashboard), navigate to *API Keys*, and create a new API key by selecting the *Single LLM* or *Dual LLM* option.

    ??? info "Example: Select Single-LLM in Dashboard"

        ![Select Single-LLM in Dashboard](../../assets/images/control/config-single-llm-dashboard.png){width="720"}

2. **Override mode via the `X-Features` header**

    Whichever Sequrity API key you use (Single-LLM or Dual-LLM),
    you can always override the mode by passing the `X-Features` header:

    - For Sequrity client, use [`FeaturesHeader.single_llm`][sequrity.control.types.headers.FeaturesHeader.single_llm] / [`FeaturesHeader.dual_llm`][sequrity.control.types.headers.FeaturesHeader.dual_llm]
    - For REST API, use the [`X-Features`](../reference/rest_api/headers/security_features.md) header

    Only the `X-Features` header is needed to switch the architecture.
    The other config headers (`X-Policy`, `X-Config`) are optional — the server
    uses preset defaults for any header not provided.

    !!! info "Specify Single-LLM via Request Headers"

        === "Sequrity Client"

            ```python hl_lines="7"
            --8<-- "examples/control/getting_started/first_message/sequrity_client.py:imports_headers"
            --8<-- "examples/control/getting_started/first_message/sequrity_client.py:single_llm"
            ```

        === "REST API"

            ```bash hl_lines="5"
            --8<-- "examples/control/getting_started/first_message/rest_api.sh:single_llm"
            ```

    !!! info "Specify Dual-LLM via Request Headers"

        === "Sequrity Client"

            ```python hl_lines="6"
            --8<-- "examples/control/getting_started/first_message/sequrity_client.py:dual_llm"
            ```

        === "REST API"

            ```bash hl_lines="5"
            --8<-- "examples/control/getting_started/first_message/rest_api.sh:dual_llm"
            ```

??? question "How is the session config built?"

    Every request to Sequrity Control runs inside a **session** governed by a session config.
    The config is built at request time through a layered pipeline:

    1. **Base config** from your API key (DB lookup) or a default preset
    2. **Header overrides** — `X-Features`, `X-Policy`, `X-Config` (all optional, applied in order)
    3. **Request-level LLM config** — model name and API key from the request body/headers

    All three config headers are independent and optional.
    You can pass any combination of them, and omitted headers simply keep their preset defaults.

    Refer to [How Session Config Is Built](../reference/bearer-token-only-vs-headers-mode.md) for details.

## Next Steps

In the examples above, Dual-LLM seems not very different from Single-LLM.
However, Dual-LLM enables advanced security features when tool calls are involved.
Learn more in [Secure Tool Use with Dual-LLM](./tool_use_dual_llm.md).

More resources explaining Security Features, Security Policies, and Fine-grained Configurations:

- See more [security features](../reference/rest_api/headers/security_features.md) like toxicity filtering and PII redaction
- Explore [security policies](../reference/rest_api/headers/security_policy.md) for fine-grained control
- Learn about [advanced configurations](../reference/rest_api/headers/security_config.md)
- See [examples](../examples/index.md) for more advanced use cases
