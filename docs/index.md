# Sequrity API

A Python client for Sequrity API.

## Installation

```bash
pip install sequrity-api
```

## Quick Start

```python
from sequrity_api import SequrityClient

client = SequrityClient(api_key="your-sequrity-api-key")

response = client.control.chat_completion(
    model="openai/gpt-5-mini",
    messages=[
        {
            "role": "user",
            "content": "What is the largest prime number below 100?",
        }
    ],
    llm_api_key="your-openrouter-key",
)
```
