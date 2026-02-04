"""
Sequrity integrations with third-party frameworks and libraries.

This package provides integration modules for using Sequrity with popular
AI/ML frameworks and tools.

Available Integrations:
    - openai_adk: AsyncOpenAI-compatible client for OpenAI Agent ADK

Example:
    >>> from sequrity_api.integrations.openai_adk import create_sequrity_openai_client
    >>> from sequrity_api.types.control.headers import FeaturesHeader
    >>>
    >>> client = create_sequrity_openai_client(
    ...     sequrity_api_key="your-key",
    ...     features=FeaturesHeader.create_dual_llm_headers()
    ... )
"""

from .openai_adk import SequrityAsyncOpenAI, create_sequrity_openai_client

__all__ = [
    "SequrityAsyncOpenAI",
    "create_sequrity_openai_client",
]
