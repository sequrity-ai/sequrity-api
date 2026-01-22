# Sequrity Client Reference

This section provides the API reference documentation for the Sequrity Python client.

## Overview

The Sequrity Python client provides a high-level interface for interacting with Sequrity's Control API. It enables secure LLM interactions with policy enforcement, including:

- **Chat Completions**: Send messages to LLMs with security features like toxicity filtering, PII redaction, and topic guardrails
- **LangGraph Integration**: Execute LangGraph workflows with Sequrity's security policies

## Quick Start

```python
from sequrity_api import SequrityClient
from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader



# Initialize the client
client = SequrityClient(api_key="your-sequrity-api-key")

# Configure security features
features = FeaturesHeader.create_single_llm_headers(
    toxicity_filter=True,
    pii_redaction=True,
)
# Configure security policy
policy = SecurityPolicyHeader.create_default()

# Make a secure chat completion request
response = client.control.create_chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4o",
    llm_api_key="your-openai-api-key",
    features=features,
    security_policy=policy,
    service_provider="openai",
)
```

## Modules

| Module | Description |
|--------|-------------|
| [Client](client.md) | Main `SequrityClient` class |
| [Control API](control.md) | `ControlAPIWrapper` for chat completions and LangGraph |
| [Headers](headers.md) | Configuration headers for features, policies, and settings |
