# Sequrity-API

Please see the full [Documentation](https://sequrity-ai.github.io/sequrity-api/)

Python client and REST API for the Sequrity API.


## Installation

```bash
pip install sequrity-api
```

## Quick Start

```python
from sequrity_api import SequrityClient
from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader

# Initialize the client
client = SequrityClient(api_key="your-sequrity-api-key")

# Create feature and policy headers
features = FeaturesHeader.create_dual_llm_header() # 💡 dual-llm
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

## Requirements

- Python 3.11+

## License

Apache 2.0
