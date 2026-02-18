# How Session Config Is Built

Every request to Sequrity Control runs inside a **session**, governed by a **session config**. The config is not a single static object — it is **built at request time** through a layered pipeline that starts from a preset and progressively applies overrides from the database, HTTP headers, and the request body.

```
Endpoint path  ──► endpoint type   (chat / code / lang-graph)
URL path       ──► provider        (openai / openrouter / anthropic / ...)
Request body   ──► model           (pllm name, or "pllm,qllm")
HTTP headers   ──► X-Features, X-Policy, X-Config, X-Api-Key
Bearer token   ──► DB lookup
```

## Config Headers Are Optional

All three config headers — `X-Features`, `X-Policy`, and `X-Config` — are **independently optional**. You can pass any combination of them:

| Header | What it controls | Required? |
|--------|-----------------|-----------|
| `X-Features` | Agent arch switch, content classifiers/blockers | No |
| `X-Policy` | Policy engine: mode, codes, auto_gen, fail_fast | No |
| `X-Config` | FSM behavior, prompt settings, response format | No |

When a header is omitted, the server uses the preset default for that part of the config (from your API key's DB entry, or the built-in preset).

**Examples of valid header combinations:**

- No config headers at all → uses all preset defaults
- Only `X-Features` → override agent arch, keep default policy and FSM config
- Only `X-Policy` → keep default arch, override policy
- `X-Features` + `X-Config` → override arch and FSM, keep default policy
- All three → full override

## Resolver Pipeline

The session config resolver runs a **four-step pipeline**:

```
1. Base config    ──► DB lookup by bearer token, or fallback to preset
2. Deep copy      ──► Prevent mutation of shared references
3. Header overrides ──► X-Features → X-Policy → X-Config (in order)
4. Request LLM config ──► model name + API key from request body / headers
```

**Step 1 — Base config:** Your Sequrity API key is looked up in the database. If a config was saved for that key, it is used as the starting point. Otherwise, a default preset is selected based on `(endpoint_type, provider, agent_arch)`.

**Step 2 — Deep copy:** A deep copy is made to prevent mutation of shared preset singletons.

**Step 3 — Header overrides:** Three optional JSON headers are applied in fixed order:

| Order | Header       | What it controls                                  |
|-------|--------------|---------------------------------------------------|
| 1     | `X-Features` | Agent arch switch, content classifiers/blockers    |
| 2     | `X-Policy`   | Policy engine: mode, codes, auto_gen, fail_fast    |
| 3     | `X-Config`   | FSM behavior, prompt settings, response format     |

!!! info "Order matters"

    `X-Features` can rebuild the entire config (e.g. switching from single-llm to dual-llm), so it runs first. `X-Policy` and `X-Config` apply on top.

**Step 4 — Request-level LLM config:** The final step applies the model name and API key from the request:

- A single model name like `"gpt-5-mini"` sets both PLLM and QLLM.
- Two model names separated by a comma like `"gpt-5-mini,gpt-5-nano"` set PLLM and QLLM independently.
- If `X-Api-Key` is provided (BYOK), the user's key is set on all LLM services matching the provider. Any model name is accepted.
- If `X-Api-Key` is **not** provided, model names are validated against the server's model allow list.

## Minimal Request (No Config Headers)

When you create a Sequrity API key in your dashboard, you already pick Single-LLM or Dual-LLM for that key, as well as other features and security policies.
Thus, you can use your Sequrity API key to retrieve those settings from the database (Step 1 of the pipeline), without specifying additional headers.

In this case, you only need to provide the Authorization token, model name, and messages.

=== "Sequrity Client"

    ```python hl_lines="5"
    from sequrity import SequrityClient

    # Initialize the client
    client = SequrityClient(api_key="your-sequrity-api-key")

    # No features, policy, or config headers needed —
    # the server uses the settings saved for your API key.
    response = client.chat.create(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini",
        llm_api_key="your-openrouter-key",
    )

    print(response.choices[0].message.content)
    ```

=== "REST API"

    ```bash hl_lines="2"
    curl -X POST https://api.sequrity.ai/control/chat/openrouter/v1/chat/completions \
    -H "Authorization: Bearer your-sequrity-api-key" \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: your-openrouter-key" \
    -d '{
        "model": "openai/gpt-5-mini",
        "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
    }'
    ```

## Overriding With Headers

You can pass any subset of config headers to override specific parts of the session config. Headers are applied as overrides (Step 3 of the pipeline) on top of the base config from your API key.

### Override only agent architecture

=== "Sequrity Client"

    ```python hl_lines="6"
    from sequrity import SequrityClient, FeaturesHeader

    client = SequrityClient(api_key="your-sequrity-api-key")

    # Only X-Features is needed to switch the architecture.
    features = FeaturesHeader.dual_llm()

    response = client.chat.create(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini",
        llm_api_key="your-openrouter-key",
        features=features,
    )
    ```

=== "REST API"

    ```bash hl_lines="5"
    curl -X POST https://api.sequrity.ai/control/chat/openrouter/v1/chat/completions \
      -H "Authorization: Bearer your-sequrity-api-key" \
      -H "Content-Type: application/json" \
      -H "X-Api-Key: your-openrouter-key" \
      -H 'X-Features: {"agent_arch":"dual-llm"}' \
      -d '{
        "model": "openai/gpt-5-mini",
        "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
      }'
    ```

### Override architecture and policy

=== "Sequrity Client"

    ```python hl_lines="6-7"
    from sequrity import SequrityClient, FeaturesHeader, SecurityPolicyHeader

    client = SequrityClient(api_key="your-sequrity-api-key")

    features = FeaturesHeader.dual_llm()
    policy = SecurityPolicyHeader.dual_llm(codes='tool "x" { must allow always; }')

    response = client.chat.create(
        messages=[{"role": "user", "content": "Hello!"}],
        model="openai/gpt-5-mini",
        llm_api_key="your-openrouter-key",
        features=features,
        security_policy=policy,
    )
    ```

=== "REST API"

    ```bash hl_lines="5-6"
    curl -X POST https://api.sequrity.ai/control/chat/openrouter/v1/chat/completions \
      -H "Authorization: Bearer your-sequrity-api-key" \
      -H "Content-Type: application/json" \
      -H "X-Api-Key: your-openrouter-key" \
      -H 'X-Features: {"agent_arch":"dual-llm"}' \
      -H 'X-Policy: {"mode":"standard","codes":"tool \"x\" { must allow always; }"}' \
      -d '{
        "model": "openai/gpt-5-mini",
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
    ```

## BYOK (Bring Your Own Key) vs Server-Managed Keys

The `X-Api-Key` header controls whether you use your own LLM provider API key or Sequrity's managed keys:

- **With `X-Api-Key` (BYOK):** Your key is used for all LLM calls to the matching provider. Any model name is accepted.
- **Without `X-Api-Key`:** Sequrity uses its own server-managed API key for the provider. Model names are validated against the server's allow list, and extra charges may apply.
