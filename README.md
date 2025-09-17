# Sequrity API

A Python client for interacting with the Sequrity API

## Build

1. Install [uv](https://docs.astral.sh/uv/)
2. Run the build command:
    ```bash
    uv build
    ```
3. The built files will be located in the `dist/` directory.

## Functionality

- Chat Completions

    Example usage:

    ```python
    import os

    from sequrity_api import SequrityClient

    client = SequrityClient(
        sequrity_api_key=os.getenv("SEQURITY_API_KEY"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        rest_api_endpoint="https://openrouter.ai/api/v1/chat/completions",
    )
    # Override the default URL for local testing
    client.sequrity_url = "http://127.0.0.1:8000"

    completion = client.create_chat_completion(
        model="openai/gpt-5-mini,openai/gpt-5-nano",
        messages=[{"role": "user", "content": "What is the capital of France?"}],
    )

    print(completion.model_dump_json(exclude_none=True, indent=2))
    ```