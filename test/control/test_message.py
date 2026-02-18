"""
Tests for Anthropic Messages API support.

This module tests the client.messages.create() method,
which sends Anthropic Messages API format requests through Sequrity's Control API.

All config headers (X-Features, X-Policy, X-Config) are optional.
The server falls back to preset defaults for any header not provided.
"""

from typing import Literal, cast

import pytest

from sequrity import SequrityClient
from sequrity.control import FeaturesHeader, FineGrainedConfigHeader, FsmOverrides
from sequrity.types.enums import LlmServiceProvider
from sequrity.types.messages.response import ToolUseBlock
from sequrity_unittest.config import get_test_config


class TestMessage:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url, timeout=300
        )

    def test_minimal(self):
        """Truly minimal request — no config headers at all.

        The server uses preset defaults from the bearer token / DB lookup.
        """
        messages = [
            {"role": "user", "content": "What is the largest prime number below 100? Answer with just the number."}
        ]
        response = self.sequrity_client.control.messages.create(
            messages=messages,
            model="claude-sonnet-4-5-20250929",
            max_tokens=256,
            llm_api_key=self.test_config.llm_api_key_anthropic,
            provider=LlmServiceProvider.ANTHROPIC,
        )

        assert response is not None
        assert response.type == "message"
        assert response.role == "assistant"
        assert len(response.content) > 0
        text_content = "".join(
            str(block.text) for block in response.content if hasattr(block, "text") and block.type == "text"
        )
        assert "97" in text_content

    @pytest.mark.parametrize("llm_mode", ["single-llm", "dual-llm"])
    def test_features_only(self, llm_mode: Literal["single-llm", "dual-llm"]):
        """Override agent arch with only X-Features — X-Policy is not required."""
        if llm_mode == "single-llm":
            features_header = FeaturesHeader.single_llm()
        else:
            features_header = FeaturesHeader.dual_llm()

        messages = [
            {"role": "user", "content": "What is the largest prime number below 100? Answer with just the number."}
        ]
        response = self.sequrity_client.control.messages.create(
            messages=messages,
            model="claude-sonnet-4-5-20250929",
            max_tokens=256,
            llm_api_key=self.test_config.llm_api_key_anthropic,
            features=features_header,
            provider=LlmServiceProvider.ANTHROPIC,
        )

        assert response is not None
        assert response.type == "message"
        assert response.role == "assistant"
        assert len(response.content) > 0
        text_content = "".join(
            str(block.text) for block in response.content if hasattr(block, "text") and block.type == "text"
        )
        assert "97" in text_content

    def test_with_system_prompt(self):
        """Test Anthropic Messages API with a system prompt."""
        messages = [{"role": "user", "content": "What do you do?"}]
        response = self.sequrity_client.control.messages.create(
            messages=messages,
            model="claude-sonnet-4-5-20250929",
            max_tokens=256,
            llm_api_key=self.test_config.llm_api_key_anthropic,
            provider=LlmServiceProvider.ANTHROPIC,
            system="You are a helpful math tutor. Always respond in exactly one sentence.",
        )

        assert response is not None
        assert len(response.content) > 0
        assert response.usage is not None
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0

    def test_with_tools(self):
        """Test Anthropic Messages API with tool definitions (dual-llm)."""
        features_header = FeaturesHeader.dual_llm()
        config_header = FineGrainedConfigHeader(fsm=FsmOverrides(max_n_turns=1))

        tools = [
            {
                "name": "get_weather",
                "description": "Get the current weather for a given location.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The city and state, e.g., San Francisco, CA"},
                    },
                    "required": ["location"],
                },
            }
        ]

        messages = [{"role": "user", "content": "What's the weather in London?"}]
        response = self.sequrity_client.control.messages.create(
            messages=messages,
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            llm_api_key=self.test_config.llm_api_key_anthropic,
            features=features_header,
            fine_grained_config=config_header,
            provider=LlmServiceProvider.ANTHROPIC,
            tools=tools,
        )

        assert response is not None
        assert len(response.content) > 0
        # Should request a tool call
        assert response.stop_reason == "tool_use"
        tool_use_blocks = [cast(ToolUseBlock, block) for block in response.content if block.type == "tool_use"]
        assert len(tool_use_blocks) > 0
        assert tool_use_blocks[0].name == "get_weather"
        assert "London" in str(tool_use_blocks[0].input)

    def test_session_tracking(self):
        """Test that session IDs are returned and can be reused."""
        messages = [{"role": "user", "content": "Hello, remember my name is Alice."}]
        response = self.sequrity_client.control.messages.create(
            messages=messages,
            model="claude-sonnet-4-5-20250929",
            max_tokens=256,
            llm_api_key=self.test_config.llm_api_key_anthropic,
            provider=LlmServiceProvider.ANTHROPIC,
        )

        assert response is not None
        assert response.session_id is not None
