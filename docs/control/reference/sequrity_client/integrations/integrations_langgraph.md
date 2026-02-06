# LangGraph

ChatOpenAI-compatible client for seamless integration with LangChain and LangGraph frameworks.

## Installation

To use the LangGraph integration, install Sequrity with the `langgraph` dependency group:

```bash
# Using pip
pip install sequrity[langgraph]

# Using uv (for development)
uv sync --group langgraph
```

This installs the required `langgraph` package along with Sequrity.

## API Reference

::: sequrity.integrations.langgraph
    options:
      show_root_heading: false
      show_source: false
      members:
        - LangGraphChatSequrityAI
        - create_sequrity_langgraph_client
