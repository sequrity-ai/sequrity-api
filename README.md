# Sequrity

Please see the full [Documentation](https://sequrity-ai.github.io/sequrity-api/)

Python client and REST API for Sequrity.


## Installation

```bash
pip install sequrity
```

## Quick Start

```python
from sequrity import SequrityClient

# Initialize the client
client = SequrityClient(api_key="your-sequrity-api-key")

# Send a chat completion request
response = client.control.create_chat_completion(
    messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
    model="openai/gpt-5-mini", # model name from your LLM provider
    llm_api_key="your-openrouter-key",
    provider="openrouter",
)

# Print the response
print(response.choices[0].message.content)
```

## Requirements

- Python 3.11+

## License

Apache 2.0
