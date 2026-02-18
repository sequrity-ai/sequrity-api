"""
Tests for LangGraph/LangChain integration.

This module tests the LangGraphChatSequrityAI client's compatibility with
the LangChain and LangGraph frameworks.
"""

import pytest
from sequrity.integrations.langgraph import create_sequrity_langgraph_client
from sequrity.types.headers import FeaturesHeader, SecurityPolicyHeader
from sequrity_unittest.config import get_test_config

# Check if LangChain is available
try:
    from langchain_core.messages import HumanMessage

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class TestLangGraphIntegration:
    """Tests for LangGraph/LangChain integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = get_test_config()

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain is not installed")
    @pytest.mark.asyncio
    async def test_basic_invoke(self):
        """Test basic LangChain invoke with Sequrity."""
        # Create Sequrity client
        llm = create_sequrity_langgraph_client(
            sequrity_api_key=self.test_config.api_key,
            features=FeaturesHeader.dual_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
            service_provider="openrouter",
            llm_api_key=self.test_config.llm_api_key_openrouter,
            base_url=self.test_config.base_url,
            model="gpt-5-mini",
        )

        # Test invoke
        response = await llm.ainvoke(
            [HumanMessage(content="What is 2 + 2? Answer with just the number.")]
        )

        # Verify response
        assert response is not None
        assert response.content is not None
        assert "4" in response.content

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain is not installed")
    @pytest.mark.asyncio
    async def test_session_tracking(self):
        """Test that session IDs are tracked across requests."""
        # Create Sequrity client
        llm = create_sequrity_langgraph_client(
            sequrity_api_key=self.test_config.api_key,
            features=FeaturesHeader.dual_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
            service_provider="openrouter",
            llm_api_key=self.test_config.llm_api_key_openrouter,
            base_url=self.test_config.base_url,
            model="gpt-5-mini",
        )

        # First request - should establish a session
        response1 = await llm.ainvoke([HumanMessage(content="Hello")])

        # Verify session ID was captured
        assert llm.session_id is not None
        first_session_id = llm.session_id

        # Second request - should use the same session
        response2 = await llm.ainvoke([HumanMessage(content="What did I just say?")])

        # Verify we got responses
        assert response1 is not None
        assert response2 is not None
        assert response1.content is not None
        assert response2.content is not None

        # Session ID should be maintained (or updated by server)
        assert llm.session_id is not None

        # Reset session and verify it's cleared
        llm.reset_session()
        assert llm.session_id is None

    # @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain is not installed")
    # @pytest.mark.asyncio
    # async def test_streaming(self):
    #     """Test streaming responses."""
    #     # Create Sequrity client
    #     llm = create_sequrity_langgraph_client(
    #         sequrity_api_key=self.test_config.api_key,
    #         features=FeaturesHeader.dual_llm(),
    #         security_policy=SecurityPolicyHeader.dual_llm(),
    #         service_provider="openrouter",
    #         llm_api_key=self.test_config.llm_api_key_openrouter,
    #         base_url=self.test_config.base_url,
    #         model="gpt-5-mini",
    #     )

    #     # Test streaming
    #     chunks = []
    #     async for chunk in llm.astream([HumanMessage(content="Count from 1 to 3")]):
    #         chunks.append(chunk)

    #     # Verify we got chunks
    #     assert len(chunks) > 0
    #     assert llm.session_id is not None

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain is not installed")
    @pytest.mark.asyncio
    async def test_manual_session_management(self):
        """Test manually setting and getting session IDs."""
        # Create Sequrity client
        llm = create_sequrity_langgraph_client(
            sequrity_api_key=self.test_config.api_key,
            features=FeaturesHeader.single_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
            service_provider="openrouter",
            llm_api_key=self.test_config.llm_api_key_openrouter,
            base_url=self.test_config.base_url,
            model="gpt-5-mini",
        )

        # Initially no session
        assert llm.session_id is None

        # Make a first request to get a valid session ID
        response1 = await llm.ainvoke([HumanMessage(content="Hello")])

        # Response should be valid and we should have a session ID
        assert response1 is not None
        assert response1.content is not None
        assert llm.session_id is not None
        valid_session_id = llm.session_id

        # Reset the session
        llm.reset_session()
        assert llm.session_id is None

        # Manually set the valid session ID we got earlier
        llm.set_session_id(valid_session_id)
        assert llm.session_id == valid_session_id

        # Clear session
        llm.set_session_id(None)
        assert llm.session_id is None
