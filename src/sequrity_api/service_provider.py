from enum import StrEnum


class LlmServiceProviderEnum(StrEnum):
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    AZURE_CREDITS = "azurecredits"
