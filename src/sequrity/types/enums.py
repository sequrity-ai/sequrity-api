"""Enumerations for Sequrity API types."""

from enum import StrEnum


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
