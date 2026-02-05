"""
Sequrity integrations with third-party frameworks and libraries.

This package provides integration modules for using Sequrity with popular
AI/ML frameworks and tools.

Available Integrations:
    - openai_agents_sdk: AsyncOpenAI-compatible client for OpenAI Agents SDK

Example:
    >>> from sequrity_api.integrations.openai_agents_sdk import create_sequrity_openai_agents_sdk_client
    >>> from sequrity_api.types.control.headers import FeaturesHeader
    >>>
    >>> client = create_sequrity_openai_agents_sdk_client(
    ...     sequrity_api_key="your-key",
    ...     features=FeaturesHeader.create_dual_llm_headers()
    ... )
"""

from .openai_agents_sdk import SequrityAsyncOpenAI, create_sequrity_openai_agents_sdk_client

__all__ = [
    "SequrityAsyncOpenAI",
    "create_sequrity_openai_agents_sdk_client",
]
