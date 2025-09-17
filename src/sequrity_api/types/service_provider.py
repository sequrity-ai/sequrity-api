from enum import StrEnum


class LlmServiceProvider(StrEnum):
    OPENAI = "openai"
    VERTEX = "vertex"
    XAI = "xai"
    # OPENROUTER = "openrouter"
    # ANTHROPIC = "anthropic"
