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
    from sequrity.control.types.headers import FeaturesHeader

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

from .langgraph import LangGraphChatSequrityAI, create_sequrity_langgraph_client
from .openai_agents_sdk import (
    SequrityAsyncOpenAI,
    create_sequrity_openai_agents_sdk_client,
)

__all__ = [
    "SequrityAsyncOpenAI",
    "create_sequrity_openai_agents_sdk_client",
    "LangGraphChatSequrityAI",
    "create_sequrity_langgraph_client",
]
