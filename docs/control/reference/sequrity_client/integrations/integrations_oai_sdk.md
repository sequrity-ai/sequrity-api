# OpenAI Agents SDK

AsyncOpenAI-compatible client for seamless integration with the OpenAI Agents SDK framework.

## Installation

To use the OpenAI Agents SDK integration, install Sequrity with the `agents` dependency group:

```bash
# Using pip
pip install sequrity[agents]

# Using uv (for development)
uv sync --group agents
```

This installs the required `openai-agents` package along with Sequrity.

## API Reference

::: sequrity.integrations.openai_agents_sdk
    options:
      show_root_heading: false
      show_source: false
      members:
        - SequrityAsyncOpenAI
        - create_sequrity_openai_agents_sdk_client
