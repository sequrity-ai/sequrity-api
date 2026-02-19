# LangGraph Integration

Execute LangGraph StateGraphs securely through Sequrity's Dual-LLM runtime with policy enforcement.

!!! note "Requirements"
    - LangGraph must be installed: `pip install langgraph`
    - Requires **Dual LLM** mode (`features.agent_arch == "dual-llm"`)
    - `strip_response_content` must be `False` in fine-grained config

---


::: sequrity.control.resources.langgraph
    options:
      show_root_heading: true
      show_source: true

---


::: sequrity.control.resources.langgraph._types.LangGraphChatCompletionRequest
    options:
      show_root_heading: true
      show_source: true

::: sequrity.control.resources.langgraph._types.LangGraphChatCompletionResponse
    options:
      show_root_heading: true
      show_source: true

---

::: sequrity.control.resources.langgraph._executor.LangGraphExecutor
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__
        - build_tool_definitions
        - execute_tool_call
