# LangGraph Integration

Execute LangGraph StateGraphs securely through Sequrity's Dual-LLM runtime with policy enforcement.

!!! note "Requirements"
    - LangGraph must be installed: `pip install langgraph`
    - Requires **Dual LLM** mode (`features.llm.feature_name == "Dual LLM"`)
    - `strip_response_content` must be `False` in fine-grained config

---


::: sequrity.control.langgraph.run_graph_sync
    options:
      show_root_heading: true
      show_source: true

---


::: sequrity.types.control.langgraph.LangGraphChatCompletionRequest
    options:
      show_root_heading: true
      show_source: true

::: sequrity.types.control.langgraph.LangGraphChatCompletionResponse
    options:
      show_root_heading: true
      show_source: true

---

::: sequrity.control.langgraph.graph_executor.LangGraphExecutor
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - build_tool_definitions
        - execute_tool_call
