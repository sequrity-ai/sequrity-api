# LangGraph Integration

Execute LangGraph StateGraphs securely through Sequrity's Dual-LLM runtime with policy enforcement.

!!! note "Requirements"
    - LangGraph must be installed: `pip install langgraph`
    - Requires **Dual LLM** mode (`features.llm.feature_name == "Dual LLM"`)
    - `strip_response_content` must be `False` in fine-grained config

---

## Core Functions

### run_graph_sync

::: sequrity_api.control.langgraph.run_graph_sync
    options:
      show_root_heading: true
      show_source: true

---

## Request/Response Types

### LangGraphChatCompletionRequest

Extended chat completion request for LangGraph execution.

::: sequrity_api.types.control.langgraph.LangGraphChatCompletionRequest
    options:
      show_root_heading: true
      show_source: true

### LangGraphChatCompletionResponse

::: sequrity_api.types.control.langgraph.LangGraphChatCompletionResponse
    options:
      show_root_heading: true
      show_source: true

---

## Graph Executor

Internal executor that compiles LangGraph to executable code and handles tool calls.

::: sequrity_api.control.langgraph.graph_executor.LangGraphExecutor
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - build_tool_definitions
        - execute_tool_call
