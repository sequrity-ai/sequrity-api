# LangGraph/LangChain Integration

This guide demonstrates how to use Sequrity with [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://github.com/langchain-ai/langchain).

## Installation

```bash
pip install sequrity langchain-openai langchain-core langgraph
```

## Basic Setup

Create a Sequrity-enabled LangGraph client:

```python
--8<-- "examples/control/integrations/langgraph_basic.py:basic-setup"
```

## Define Tools

```python
--8<-- "examples/control/integrations/langgraph_basic.py:define-tools"
```

## Build Graph

```python
--8<-- "examples/control/integrations/langgraph_basic.py:build-graph"
```

## Run the Graph

```python
--8<-- "examples/control/integrations/langgraph_basic.py:run-graph"
```

## Complete Example

See the complete working example at [`examples/control/integrations/langgraph_basic.py`](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/integrations/langgraph_basic.py).

## See Also

- [FeaturesHeader Documentation](../reference/sequrity_client/headers/features_header.md)
- [SecurityPolicyHeader Documentation](../reference/sequrity_client/headers/policy_header.md)
- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
