import os
from dataclasses import dataclass

from sequrity._constants import SEQURITY_API_URL
from sequrity.types.enums import LlmServiceProvider

DEFAULT_TEST_MODEL: dict[LlmServiceProvider | None, str] = {
    None: "google/gemini-3-flash-preview",
    LlmServiceProvider.OPENAI: "gpt-5-mini",
    LlmServiceProvider.OPENROUTER: "google/gemini-3-flash-preview",
    LlmServiceProvider.ANTHROPIC: "claude-sonnet-4-5",
    LlmServiceProvider.SEQURITY_AZURE: "gpt-5-mini",
}


@dataclass
class TestConfig:
    test_mode: str
    api_key: str | None
    llm_api_key_openai: str | None
    llm_api_key_openrouter: str | None
    llm_api_key_anthropic: str | None
    llm_api_key_sequrity_azure: str | None
    base_url: str

    def get_model_name(self, service_provider: LlmServiceProvider | None):
        return DEFAULT_TEST_MODEL[service_provider]

    def get_llm_api_key(self, service_provider: LlmServiceProvider | None):
        if service_provider == LlmServiceProvider.OPENAI:
            return self.llm_api_key_openai
        elif service_provider == LlmServiceProvider.OPENROUTER:
            return self.llm_api_key_openrouter
        elif service_provider == LlmServiceProvider.ANTHROPIC:
            return self.llm_api_key_anthropic
        elif service_provider == LlmServiceProvider.SEQURITY_AZURE:
            return self.llm_api_key_sequrity_azure
        elif service_provider is None:
            return self.llm_api_key_openrouter
        else:
            raise ValueError(
                f"No LLM API key configured for service provider: {service_provider}"
            )


def get_test_config():
    test_mode = os.getenv("TEST_MODE", "remote")
    api_key = os.getenv("SEQURITY_API_KEY")
    llm_api_key_openai = os.getenv("OPENAI_API_KEY")
    llm_api_key_openrouter = os.getenv("OPENROUTER_API_KEY")
    llm_api_key_anthropic = os.getenv("ANTHROPIC_API_KEY")
    llm_api_key_sequrity_azure = os.getenv("SEQURITY_AZURE_API_KEY")

    assert api_key is not None, (
        "SEQURITY_API_KEY must be set in environment variables for tests."
    )
    assert llm_api_key_openai is not None, (
        "OPENAI_API_KEY must be set in environment variables for tests."
    )
    assert llm_api_key_openrouter is not None, (
        "OPENROUTER_API_KEY must be set in environment variables for tests."
    )
    assert llm_api_key_anthropic is not None, (
        "ANTHROPIC_API_KEY must be set in environment variables for tests."
    )
    assert llm_api_key_sequrity_azure is not None, (
        "SEQURITY_AZURE_API_KEY must be set in environment variables for tests."
    )

    if test_mode == "local":
        base_url = os.getenv("SEQURITY_BASE_URL", "http://localhost:8000")
    else:
        base_url = SEQURITY_API_URL

    return TestConfig(
        test_mode=test_mode,
        api_key=api_key,
        llm_api_key_openai=llm_api_key_openai,
        llm_api_key_openrouter=llm_api_key_openrouter,
        llm_api_key_anthropic=llm_api_key_anthropic,
        llm_api_key_sequrity_azure=llm_api_key_sequrity_azure,
        base_url=base_url,
    )
