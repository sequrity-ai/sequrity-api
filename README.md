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

sequrity_key = "<your-sequrity-api-key>"
openrouter_key = "<your-openrouter-key>"

client = SequrityClient(api_key=sequrity_key)

response = client.chat.create(
    messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
    model="openai/gpt-5-mini", # model name on OpenRouter
    llm_api_key=openrouter_key,
    provider="openrouter",
)

# Print the response
print(response.choices[0].message.content)
```

## Requirements

- Python 3.11+

## License

Apache 2.0
