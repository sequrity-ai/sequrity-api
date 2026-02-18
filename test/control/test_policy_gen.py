"""
Tests for Policy Generation support.

This module tests the client.policy.generate() method,
which generates SQRT security policies from natural language descriptions.
"""

import pytest

from sequrity import LlmServiceProvider, SequrityClient
from sequrity.control._constants import build_policy_gen_url
from sequrity.control.types.policy_gen import (
    PolicyGenRequestAnthropicMessages,
    PolicyGenRequestOpenAiChatCompletion,
    PolicyGenRequestOpenRouterChatCompletion,
    PolicyGenRequestSequrityAzureChatCompletion,
    PolicyGenRequestSequrityAzureResponses,
    PolicyGenResponse,
)
from sequrity_unittest.config import get_test_config

# -- OpenAI / OpenRouter / Azure Chat Completion tool format ------------------

OAI_READ_FILE_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file given its path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to read."},
            },
            "required": ["path"],
        },
    },
}

OAI_DELETE_FILE_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "delete_file",
        "description": "Delete a file given its path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to delete."},
            },
            "required": ["path"],
        },
    },
}

OAI_SEND_EMAIL_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Send an email to a recipient.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address."},
                "subject": {"type": "string", "description": "Email subject."},
                "body": {"type": "string", "description": "Email body content."},
            },
            "required": ["to", "subject", "body"],
        },
    },
}

# -- Anthropic Messages tool format -------------------------------------------

ANTHROPIC_WEB_SEARCH_TOOL: dict = {
    "name": "web_search",
    "description": "Search the web for information.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query."},
        },
        "required": ["query"],
    },
}

ANTHROPIC_WRITE_FILE_TOOL: dict = {
    "name": "write_file",
    "description": "Write content to a file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "The file path."},
            "content": {"type": "string", "description": "The content to write."},
        },
        "required": ["path", "content"],
    },
}


class TestPolicyGeneration:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url, timeout=300
        )

    def test_openai_chat_completion_format(self):
        """Test policy generation with OpenAI Chat Completion tool format."""
        request = PolicyGenRequestOpenAiChatCompletion.model_validate(
            {
                "model": self.test_config.get_model_name(LlmServiceProvider.OPENAI),
                "description": "Allow the agent to read files but prevent it from deleting any files.",
                "tools": [OAI_READ_FILE_TOOL, OAI_DELETE_FILE_TOOL],
            }
        )

        response = self.sequrity_client.control.policy.generate(
            request=request,
            llm_api_key=self.test_config.get_llm_api_key(LlmServiceProvider.OPENAI),
        )

        assert isinstance(response, PolicyGenResponse)
        assert response.policies is not None
        assert len(response.policies) > 0
        assert response.usage is not None
        assert "prompt_tokens" in response.usage
        assert "completion_tokens" in response.usage
        assert "total_tokens" in response.usage
        print("Generated policy:", response.policies)

    def test_openrouter_chat_completion_format(self):
        """Test policy generation with OpenRouter Chat Completion tool format."""
        request = PolicyGenRequestOpenRouterChatCompletion.model_validate(
            {
                "model": self.test_config.get_model_name(LlmServiceProvider.OPENROUTER),
                "description": "Only allow the agent to send emails to addresses ending in @company.com.",
                "tools": [OAI_SEND_EMAIL_TOOL],
            }
        )

        response = self.sequrity_client.control.policy.generate(
            request=request,
            llm_api_key=self.test_config.get_llm_api_key(LlmServiceProvider.OPENROUTER),
        )

        assert isinstance(response, PolicyGenResponse)
        assert response.policies is not None
        assert len(response.policies) > 0
        print("Generated policy:", response.policies)

    def test_anthropic_messages_format(self):
        """Test policy generation with Anthropic Messages tool format."""
        request = PolicyGenRequestAnthropicMessages.model_validate(
            {
                "model": self.test_config.get_model_name(LlmServiceProvider.ANTHROPIC),
                "description": "Allow the agent to search the web but block any file operations.",
                "tools": [ANTHROPIC_WEB_SEARCH_TOOL, ANTHROPIC_WRITE_FILE_TOOL],
            }
        )

        response = self.sequrity_client.control.policy.generate(
            request=request,
            llm_api_key=self.test_config.get_llm_api_key(LlmServiceProvider.ANTHROPIC),
        )

        assert isinstance(response, PolicyGenResponse)
        assert response.policies is not None
        assert len(response.policies) > 0
        print("Generated policy:", response.policies)

    def test_sequrity_azure_chat_completion_format(self):
        """Test policy generation with Sequrity Azure Chat Completion tool format."""
        request = PolicyGenRequestSequrityAzureChatCompletion.model_validate(
            {
                "model": self.test_config.get_model_name(None),
                "description": "Allow the agent to read files but prevent it from deleting any files.",
                "tools": [OAI_READ_FILE_TOOL],
            }
        )

        response = self.sequrity_client.control.policy.generate(
            request=request,
            llm_api_key=self.test_config.get_llm_api_key(LlmServiceProvider.SEQURITY_AZURE),
        )

        assert isinstance(response, PolicyGenResponse)
        assert response.policies is not None
        assert len(response.policies) > 0
        print("Generated policy:", response.policies)


class TestPolicyGenUrlRouting:
    """Unit tests for provider-specific URL routing."""

    BASE = "https://api.sequrity.ai"

    def test_oai_chat_completion_routes_to_openai(self):
        assert build_policy_gen_url(self.BASE, "oai_chat_completion") == (
            f"{self.BASE}/control/policy-gen/openai/v1/generate"
        )

    def test_openrouter_routes_to_default(self):
        assert build_policy_gen_url(self.BASE, "openrouter_chat_completion") == (
            f"{self.BASE}/control/policy-gen/v1/generate"
        )

    def test_anthropic_routes_to_anthropic(self):
        assert build_policy_gen_url(self.BASE, "anthropic_messages") == (
            f"{self.BASE}/control/policy-gen/anthropic/v1/generate"
        )

    def test_sequrity_azure_chat_completion_routes_to_sequrity_azure(self):
        assert build_policy_gen_url(self.BASE, "sequrity_azure_chat_completion") == (
            f"{self.BASE}/control/policy-gen/sequrity_azure/v1/generate"
        )

    def test_sequrity_azure_responses_routes_to_sequrity_azure(self):
        assert build_policy_gen_url(self.BASE, "sequrity_azure_responses") == (
            f"{self.BASE}/control/policy-gen/sequrity_azure/v1/generate"
        )

    def test_unknown_type_falls_back_to_default(self):
        assert build_policy_gen_url(self.BASE, "some_future_type") == (f"{self.BASE}/control/policy-gen/v1/generate")
