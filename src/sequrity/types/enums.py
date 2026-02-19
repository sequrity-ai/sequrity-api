"""Enumerations for Sequrity API types."""

from enum import StrEnum
from typing import Literal


class RestApiType(StrEnum):
    """REST API style for the request/response format."""

    CHAT_COMPLETIONS = "chat_completions"
    MESSAGES = "messages"
    RESPONSES = "responses"


class LlmServiceProvider(StrEnum):
    """LLM service provider identifiers.

    Attributes:
        OPENAI: [OpenAI](https://openai.com/) service provider.
        OPENROUTER: [OpenRouter](https://openrouter.ai/) service provider.
        ANTHROPIC: [Anthropic](https://anthropic.com/) service provider.
    """

    OPENAI = "openai"
    OPENROUTER = "openrouter"
    ANTHROPIC = "anthropic"
    SEQURITY_AZURE = "sequrity_azure"


LlmServiceProviderStr = Literal["openai", "openrouter", "anthropic", "sequrity_azure"]
