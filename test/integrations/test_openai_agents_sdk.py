"""
Tests for OpenAI Agents SDK integration.

This module tests the SequrityAsyncOpenAI client's compatibility with
the OpenAI Agents SDK framework.
"""

import os

import pytest

from sequrity.control import FeaturesHeader, SecurityPolicyHeader
from sequrity.control.integrations.openai_agents_sdk import create_sequrity_openai_agents_sdk_client
from sequrity_unittest.config import get_test_config


# Check if OpenAI Agents SDK is available
try:
    from agents import Agent, Runner, RunConfig

    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False


class TestOpenAIAgentsSDKIntegration:
    """Tests for OpenAI Agents SDK integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = get_test_config()

    @pytest.mark.skipif(not AGENTS_AVAILABLE, reason="OpenAI Agents SDK is not installed")
    @pytest.mark.asyncio
    async def test_basic_agent_with_sequrity(self):
        """Test basic agent execution with Sequrity dual-LLM."""
        # Create Sequrity client with dual-LLM features
        client = create_sequrity_openai_agents_sdk_client(
            sequrity_api_key=self.test_config.api_key,
            features=FeaturesHeader.dual_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
            service_provider="openrouter",
            llm_api_key=self.test_config.llm_api_key_openrouter,
            base_url=self.test_config.base_url,
        )

        # Create a simple agent
        agent = Agent(
            name="TestAgent",
            instructions="You are a helpful assistant. Keep responses very concise (one sentence).",
        )

        # Configure the run with Sequrity provider
        run_config = RunConfig(
            model="gpt-5-mini",
            model_provider=client,
        )

        # Disable tracing for cleaner test output
        os.environ["OPENAI_AGENTS_TRACE_ENABLED"] = "false"

        # Run the agent
        result = await Runner.run(
            agent,
            input="What is 2 + 2?",
            run_config=run_config,
        )

        # Verify response
        assert result is not None
        assert result.final_output is not None
        assert len(result.final_output) > 0
        # Check that the response mentions 4
        assert "4" in result.final_output

    @pytest.mark.skipif(not AGENTS_AVAILABLE, reason="OpenAI Agents SDK is not installed")
    @pytest.mark.asyncio
    async def test_session_tracking(self):
        """Test that session IDs are tracked across multiple requests."""
        # Create Sequrity client
        client = create_sequrity_openai_agents_sdk_client(
            sequrity_api_key=self.test_config.api_key,
            features=FeaturesHeader.dual_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
            service_provider="openrouter",
            llm_api_key=self.test_config.llm_api_key_openrouter,
            base_url=self.test_config.base_url,
        )

        # Create a simple agent
        agent = Agent(
            name="SessionTestAgent",
            instructions="You are a helpful assistant.",
        )

        # Configure the run
        run_config = RunConfig(
            model="gpt-5-mini",
            model_provider=client,
        )

        # Disable tracing
        os.environ["OPENAI_AGENTS_TRACE_ENABLED"] = "false"

        # First request - should establish a session
        result1 = await Runner.run(
            agent,
            input="Hello",
            run_config=run_config,
        )

        # Verify session ID was captured
        assert client.session_id is not None
        first_session_id = client.session_id

        # Second request - should use the same session
        result2 = await Runner.run(
            agent,
            input="What did I just say?",
            run_config=run_config,
        )

        # Verify we got responses
        assert result1 is not None
        assert result2 is not None
        assert result1.final_output is not None
        assert result2.final_output is not None

        # Session ID should be maintained (or updated by server)
        assert client.session_id is not None

        # Reset session and verify it's cleared
        client.reset_session()
        assert client.session_id is None

    @pytest.mark.asyncio
    async def test_direct_chat_completion(self):
        """Test direct chat.completions.create() without Agent ADK."""
        # Create Sequrity client
        client = create_sequrity_openai_agents_sdk_client(
            sequrity_api_key=self.test_config.api_key,
            features=FeaturesHeader.dual_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
            service_provider="openrouter",
            llm_api_key=self.test_config.llm_api_key_openrouter,
            base_url=self.test_config.base_url,
        )

        # Make a direct chat completion request
        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": "What is the capital of France?"}],
        )

        # Verify response
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        assert "Paris" in response.choices[0].message.content

        # Verify session ID was captured
        assert client.session_id is not None

    @pytest.mark.asyncio
    async def test_manual_session_management(self):
        """Test manually setting and getting session IDs."""
        # Create Sequrity client
        client = create_sequrity_openai_agents_sdk_client(
            sequrity_api_key=self.test_config.api_key,
            features=FeaturesHeader.single_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
            service_provider="openrouter",
            llm_api_key=self.test_config.llm_api_key_openrouter,
            base_url=self.test_config.base_url,
        )

        # Initially no session
        assert client.session_id is None

        # Make a first request to get a valid session ID
        response1 = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": "Hello"}],
        )

        # Response should be valid and we should have a session ID
        assert response1 is not None
        assert len(response1.choices) > 0
        assert client.session_id is not None
        valid_session_id = client.session_id

        # Reset the session
        client.reset_session()
        assert client.session_id is None

        # Manually set the valid session ID we got earlier
        client.set_session_id(valid_session_id)
        assert client.session_id == valid_session_id

        # Make another request - should use the session ID we set
        response2 = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": "What did I say?"}],
        )

        # Response should be valid
        assert response2 is not None
        assert len(response2.choices) > 0

        # Session ID should still be set
        assert client.session_id is not None

        # Clear session
        client.set_session_id(None)
        assert client.session_id is None
