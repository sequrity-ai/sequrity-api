# LangGraph/LangChain Integration

This guide demonstrates how to use Sequrity with [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://github.com/langchain-ai/langchain).


## Basic Usage

```python
from sequrity.integrations.langgraph import create_sequrity_langgraph_client
from sequrity.control.types.headers import FeaturesHeader, SecurityPolicyHeader

# Create client
llm = create_sequrity_langgraph_client(
    sequrity_api_key="your-key",
    features=FeaturesHeader.dual_llm(),
    security_policy=SecurityPolicyHeader.dual_llm()
)

# Use with LangChain
response = llm.invoke([{"role": "user", "content": "Hello!"}])
```

## LangGraph Example

```python
from sequrity.integrations.langgraph import create_sequrity_langgraph_client
from sequrity.control.types.headers import FeaturesHeader
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool

# Create client
llm = create_sequrity_langgraph_client(
    sequrity_api_key="your-key",
    features=FeaturesHeader.dual_llm()
)

# Define tools and bind to LLM
@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

llm_with_tools = llm.bind_tools([search])

# Build graph
def chatbot(state):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph = StateGraph({"messages": list})
graph.add_node("chatbot", chatbot)
graph.add_node("tools", ToolNode([search]))
graph.add_conditional_edges("chatbot", tools_condition)
graph.add_edge("tools", "chatbot")
graph.add_edge(START, "chatbot")

# Run
app = graph.compile()
for event in app.stream({"messages": [{"role": "user", "content": "Search for LangGraph"}]}):
    print(event)
```

## Session Management

```python
llm = create_sequrity_langgraph_client(sequrity_api_key="your-key")

# Session tracked automatically
llm.invoke([{"role": "user", "content": "My name is Alice"}])
print(llm.session_id)

# Reset for new conversation
llm.reset_session()
```

## See Also

- [FeaturesHeader Documentation](../reference/sequrity_client/headers/features_header.md)
- [SecurityPolicyHeader Documentation](../reference/sequrity_client/headers/policy_header.md)
- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
