"""
Sequrity integrations with third-party frameworks and libraries.

This package provides integration modules for using Sequrity with popular
AI/ML frameworks and tools.

Available Integrations:
    - openai_agents_sdk: AsyncOpenAI-compatible client for OpenAI Agents SDK
    - langgraph: ChatOpenAI-compatible client for LangChain/LangGraph

Example:
    ```python
    from sequrity.integrations.openai_agents_sdk import create_sequrity_openai_agents_sdk_client
    from sequrity.integrations.langgraph import create_sequrity_langgraph_client
    from sequrity import FeaturesHeader

    # OpenAI Agents SDK
    client = create_sequrity_openai_agents_sdk_client(
        sequrity_api_key="your-key",
        features=FeaturesHeader.dual_llm()
    )

    # LangGraph
    llm = create_sequrity_langgraph_client(
        sequrity_api_key="your-key",
        features=FeaturesHeader.dual_llm()
    )
    ```
"""


def __getattr__(name: str):
    """Lazy imports to avoid requiring optional dependencies at package import time."""
    if name in ("SequrityAsyncOpenAI", "create_sequrity_openai_agents_sdk_client"):
        from .openai_agents_sdk import SequrityAsyncOpenAI, create_sequrity_openai_agents_sdk_client

        return {
            "SequrityAsyncOpenAI": SequrityAsyncOpenAI,
            "create_sequrity_openai_agents_sdk_client": create_sequrity_openai_agents_sdk_client,
        }[name]
    if name in ("LangGraphChatSequrityAI", "create_sequrity_langgraph_client"):
        from .langgraph import LangGraphChatSequrityAI, create_sequrity_langgraph_client

        return {
            "LangGraphChatSequrityAI": LangGraphChatSequrityAI,
            "create_sequrity_langgraph_client": create_sequrity_langgraph_client,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "SequrityAsyncOpenAI",
    "create_sequrity_openai_agents_sdk_client",
    "LangGraphChatSequrityAI",
    "create_sequrity_langgraph_client",
]
