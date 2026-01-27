import os
from dataclasses import dataclass
from typing import Literal

from sequrity.constants import SEQURITY_API_URL
from sequrity.service_provider import LlmServiceProviderEnum

DEFAULT_TEST_MODEL = {
    "default": "google/gemini-3-flash-preview",
    LlmServiceProviderEnum.OPENAI: "gpt-5-mini",
    LlmServiceProviderEnum.OPENROUTER: "google/gemini-3-flash-preview",
    LlmServiceProviderEnum.AZURE_CREDITS: "gpt-5-mini",
}


@dataclass
class TestConfig:
    test_mode: str
    api_key: str | None
    llm_api_key_openai: str | None
    llm_api_key_openrouter: str | None
    llm_api_key_azurecredits: str | None
    base_url: str

    def get_model_name(self, service_provider: LlmServiceProviderEnum | Literal["default"]):
        return DEFAULT_TEST_MODEL[service_provider]

    def get_llm_api_key(self, service_provider: LlmServiceProviderEnum | Literal["default"]):
        if service_provider == LlmServiceProviderEnum.OPENAI:
            return self.llm_api_key_openai
        elif service_provider == LlmServiceProviderEnum.OPENROUTER:
            return self.llm_api_key_openrouter
        elif service_provider == LlmServiceProviderEnum.AZURE_CREDITS:
            return self.llm_api_key_azurecredits
        elif service_provider == "default":
            return self.llm_api_key_openrouter
        else:
            raise ValueError(f"No LLM API key configured for service provider: {service_provider}")


def get_test_config():
    test_mode = os.getenv("TEST_MODE", "remote")
    api_key = os.getenv("SEQURITY_API_KEY")
    llm_api_key_openai = os.getenv("OPENAI_API_KEY")
    llm_api_key_openrouter = os.getenv("OPENROUTER_API_KEY")
    llm_api_key_azurecredits = os.getenv("AZURE_CREDITS_API_KEY")

    assert api_key is not None, "SEQURITY_API_KEY must be set in environment variables for tests."
    assert llm_api_key_openai is not None, "OPENAI_API_KEY must be set in environment variables for tests."
    assert llm_api_key_openrouter is not None, "OPENROUTER_API_KEY must be set in environment variables for tests."
    assert llm_api_key_azurecredits is not None, "AZURE_CREDITS_API_KEY must be set in environment variables for tests."

    if test_mode == "local":
        base_url = os.getenv("SEQURITY_BASE_URL", "http://localhost:8000")
    else:
        base_url = SEQURITY_API_URL

    return TestConfig(
        test_mode=test_mode,
        api_key=api_key,
        llm_api_key_openai=llm_api_key_openai,
        llm_api_key_openrouter=llm_api_key_openrouter,
        llm_api_key_azurecredits=llm_api_key_azurecredits,
        base_url=base_url,
    )
