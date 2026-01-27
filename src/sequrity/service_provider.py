from enum import StrEnum


class LlmServiceProviderEnum(StrEnum):
    """
    Enum representing different LLM service providers.

    Attributes:
        OPENAI (str): Represents the [OpenAI](https://openai.com/) service provider.
        OPENROUTER (str): Represents the [OpenRouter](https://openrouter.ai/) service provider.
        AZURE_CREDITS (str): Represents LLM deployed on [Azure](https://azure.microsoft.com/), which is not available for now.
    """

    OPENAI = "openai"
    OPENROUTER = "openrouter"
    AZURE_CREDITS = "azurecredits"
