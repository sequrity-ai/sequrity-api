# Bearer-Token-only vs Headers-Mode

When making requests to the Sequrity Control API, you have two options for specifying security features, policies, and fine-grained configurations: Bearer-Token-only mode and Headers-mode.

| Mode | Required Headers | Optional Headers |
| ---- | ---------------- | ---------------- |
| Bearer-Token-only | `Authorization: Bearer <sequrity-api-key>` | `X-Api-Key`, `X-Session-Id` |
| Headers | `Authorization: Bearer <sequrity-api-key>`, `X-Security-Features`, `X-Security-Policy` | `X-Security-Config`, `X-Api-Key`, `X-Session-Id` |

!!! top "Experimental"

    For now, only headers-mode supports fine-grained configurations.

## Bearer-Token-only mode

When you create a Sequrity API key in your dashboard, you already pick Single-LLM or Dual-LLM for that key, as well as other features and security policies.
Thus, you can also just use your Sequrity API key to retrieve those settings, without specifying additional headers. This is called Bearer-Token-only mode.

=== "Sequrity Client"

    ```python hl_lines="5 13"
    from sequrity_api import SequrityClient
    from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader

    # Initialize the client
    client = SequrityClient(api_key="your-sequrity-api-key")

    # 💡 `features` and `security_policy` are not needed in Bearer-Token-only mode

    # Send a chat completion request
    response = client.control.create_chat_completion(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini", # model name from your LLM provider
        llm_api_key="your-openrouter-key",
        service_provider="openrouter",
    )

    # Print the response
    print(response.choices[0].message.content)
    ```

=== "REST API"

    ```bash hl_lines="2 4"
    curl -X POST https://api.sequrity.ai/control/v1/chat/completions \
    -H "Authorization: Bearer your-sequrity-api-key" \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: your-openrouter-key" \
    -d '{
        "model": "openai/gpt-5-mini",
        "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
    }'
    ```

## Headers-mode

You can also specify security features and policies in the request headers, as shown in the previous examples.
Note that both security features and policies must be specified together in headers-mode.
In this case, the settings in the request headers will override those attached to your Sequrity API key.


=== "Sequrity Client"

    ```python hl_lines="5 15-17"
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
        service_provider="openrouter",
    )

    # Print the response
    print(response.choices[0].message.content)
    ```

=== "REST API"

    ```bash hl_lines="2 5-6"
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


