"""
LangChain/LangGraph integration for Sequrity Control.

This module provides a ChatOpenAI-compatible client that routes requests through
Sequrity's secure orchestrator with automatic session management and security features.

Example:
    ```python
    from sequrity.control.integrations.langgraph import create_sequrity_langgraph_client
    from sequrity.control import FeaturesHeader, SecurityPolicyHeader

    # Create client with Sequrity security features
    llm = create_sequrity_langgraph_client(
        sequrity_api_key="your-sequrity-key",
        features=FeaturesHeader.dual_llm(),
        security_policy=SecurityPolicyHeader.dual_llm()
    )

    # Use with LangChain
    response = llm.invoke([{"role": "user", "content": "Hello!"}])

    # Use with LangGraph
    from langgraph.graph import StateGraph
    llm_with_tools = llm.bind_tools([...])
    # ... build your graph
    ```
"""

import json
import os
from typing import Any, AsyncIterator, Iterator

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_openai import ChatOpenAI

from .._constants import SEQURITY_BASE_URL, build_control_base_url, build_sequrity_headers
from ..types.enums import EndpointType
from ...types.enums import LlmServiceProvider, LlmServiceProviderStr
from ..types.headers import (
    FeaturesHeader,
    FineGrainedConfigHeader,
    SecurityPolicyHeader,
)


class LangGraphChatSequrityAI(ChatOpenAI):
    """
    ChatOpenAI client configured to route requests through Sequrity's secure orchestrator.

    This client is a drop-in replacement for ChatOpenAI that automatically:
    - Adds Sequrity security headers (features, policies, configuration)
    - Tracks session IDs across multiple requests
    - Routes to Sequrity's API endpoint

    The client maintains session state across multiple chat completion requests,
    which is essential for Sequrity's dual-LLM architecture to maintain context.

    Args:
        sequrity_api_key: Sequrity API key (used as bearer token)
        features: Security features configuration (LLM mode, taggers, constraints)
        security_policy: Security policy configuration (SQRT/Cedar policies)
        fine_grained_config: Fine-grained session configuration
        service_provider: LLM service provider (openai, openrouter, anthropic)
        llm_api_key: Optional API key for the LLM provider
        base_url: Sequrity base URL (default: https://api.sequrity.ai)
        endpoint_type: Endpoint type (chat, code, lang-graph). Defaults to chat.
        model: Model name to use (default: gpt-4)
        **kwargs: Additional arguments passed to ChatOpenAI

    Example:
        ```python
        features = FeaturesHeader.dual_llm()

        llm = LangGraphChatSequrityAI(
            sequrity_api_key="your-key",
            features=features,
        )

        # Session ID is automatically tracked
        response1 = llm.invoke([{"role": "user", "content": "Hello"}])
        response2 = llm.invoke([{"role": "user", "content": "Continue"}])  # Uses same session
        ```
    """

    _session_id: str | None = None  # Internal session ID storage

    def __init__(
        self,
        sequrity_api_key: str,
        features: FeaturesHeader | None = None,
        security_policy: SecurityPolicyHeader | None = None,
        fine_grained_config: FineGrainedConfigHeader | None = None,
        service_provider: LlmServiceProvider | LlmServiceProviderStr = LlmServiceProvider.OPENROUTER,
        llm_api_key: str | None = None,
        base_url: str | None = None,
        endpoint_type: EndpointType | str = EndpointType.CHAT,
        model: str = "gpt-4",
        **kwargs: Any,
    ):
        """Initialize Sequrity-enabled LangGraph ChatOpenAI client."""
        if base_url is None:
            base_url = os.getenv("SEQURITY_BASE_URL", SEQURITY_BASE_URL)
        # Build custom headers using shared builder
        custom_headers = build_sequrity_headers(
            api_key=sequrity_api_key,
            llm_api_key=llm_api_key,
            features=features.dump_for_headers(mode="json_str") if features else None,
            policy=security_policy.dump_for_headers(mode="json_str") if security_policy else None,
            config=fine_grained_config.dump_for_headers(mode="json_str") if fine_grained_config else None,
        )

        # Merge with any user-provided headers
        if "default_headers" not in kwargs:
            kwargs["default_headers"] = {}
        kwargs["default_headers"].update(custom_headers)

        # Enable response headers to extract session ID
        if "include_response_headers" not in kwargs:
            kwargs["include_response_headers"] = True

        # Construct Sequrity API endpoint URL with service provider
        sequrity_base_url = build_control_base_url(base_url, endpoint_type, service_provider)

        # Set base_url and model in kwargs for parent class
        kwargs["base_url"] = sequrity_base_url
        kwargs["model"] = model
        kwargs["api_key"] = sequrity_api_key

        # Initialize parent class
        super().__init__(
            **kwargs,
        )

    def _unwrap_sequrity_response(self, result: ChatResult) -> ChatResult:
        """
        Unwrap Sequrity dual-LLM JSON response format.

        Sequrity's dual-LLM returns responses in the format:
        {"status": "success", "final_return_value": {"value": "...", "meta": {...}}}

        This method extracts the actual content from the wrapper.
        Only unwraps if there are no tool calls (tool calls should not be unwrapped).
        """
        if not result.generations:
            return result

        for generation in result.generations:
            if isinstance(generation, ChatGeneration) and isinstance(generation.message, AIMessage):
                # Don't unwrap if there are tool calls - they're already in the correct format
                if generation.message.tool_calls:
                    continue

                content = generation.message.content

                # Try to parse as JSON to detect Sequrity wrapper
                if isinstance(content, str) and content:
                    try:
                        parsed = json.loads(content)
                        # Check if it's a Sequrity dual-LLM response
                        if isinstance(parsed, dict):
                            if "status" in parsed and "final_return_value" in parsed:
                                # Extract the actual value
                                if parsed["status"] == "success":
                                    final_value = parsed["final_return_value"]["value"]
                                    # Update the message content with unwrapped value
                                    generation.message.content = (
                                        str(final_value) if not isinstance(final_value, str) else final_value
                                    )
                                elif parsed["status"] == "failure":
                                    # Handle error responses
                                    error_msg = parsed.get("error", {}).get("message", "Unknown error")
                                    generation.message.content = f"Error: {error_msg}"
                    except (json.JSONDecodeError, KeyError, TypeError):
                        # Not a JSON response or not in expected format, leave as is
                        pass

        return result

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Override _generate to extract and reuse session IDs and unwrap Sequrity responses."""
        # Add session ID to extra_headers if we have one
        if self._session_id is not None:
            if "extra_headers" not in kwargs:
                kwargs["extra_headers"] = {}
            kwargs["extra_headers"]["X-Session-ID"] = self._session_id

        # Call parent's _generate method
        result = super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

        # Extract session ID from generation_info if present
        if result.generations and len(result.generations) > 0:
            gen_info = result.generations[0].generation_info
            if gen_info and "headers" in gen_info:
                session_id = gen_info["headers"].get("x-session-id") or gen_info["headers"].get("X-Session-ID")
                if session_id:
                    self._session_id = session_id

        # Unwrap Sequrity dual-LLM response format
        result = self._unwrap_sequrity_response(result)

        return result

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Override _agenerate to extract and reuse session IDs and unwrap Sequrity responses (async version)."""
        # Add session ID to extra_headers if we have one
        if self._session_id is not None:
            if "extra_headers" not in kwargs:
                kwargs["extra_headers"] = {}
            kwargs["extra_headers"]["X-Session-ID"] = self._session_id

        # Call parent's _agenerate method
        result = await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)

        # Extract session ID from generation_info if present
        if result.generations and len(result.generations) > 0:
            gen_info = result.generations[0].generation_info
            if gen_info and "headers" in gen_info:
                session_id = gen_info["headers"].get("x-session-id") or gen_info["headers"].get("X-Session-ID")
                if session_id:
                    self._session_id = session_id

        # Unwrap Sequrity dual-LLM response format
        result = self._unwrap_sequrity_response(result)

        return result

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Override _stream to extract and reuse session IDs."""
        # Add session ID to extra_headers if we have one
        if self._session_id:
            if "extra_headers" not in kwargs:
                kwargs["extra_headers"] = {}
            kwargs["extra_headers"]["X-Session-ID"] = self._session_id

        # Call parent's _stream method and extract session ID from first chunk
        is_first_chunk = True
        for chunk in super()._stream(messages, stop=stop, run_manager=run_manager, **kwargs):
            # Extract session ID from the first chunk's generation_info
            if is_first_chunk and chunk.generation_info and "headers" in chunk.generation_info:
                session_id = chunk.generation_info["headers"].get("x-session-id") or chunk.generation_info[
                    "headers"
                ].get("X-Session-ID")
                if session_id:
                    self._session_id = session_id
                is_first_chunk = False
            yield chunk

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Override _astream to extract and reuse session IDs (async version)."""
        # Add session ID to extra_headers if we have one
        if self._session_id:
            if "extra_headers" not in kwargs:
                kwargs["extra_headers"] = {}
            kwargs["extra_headers"]["X-Session-ID"] = self._session_id

        # Call parent's _astream method and extract session ID from first chunk
        is_first_chunk = True
        async for chunk in super()._astream(messages, stop=stop, run_manager=run_manager, **kwargs):
            # Extract session ID from the first chunk's generation_info
            if is_first_chunk and chunk.generation_info and "headers" in chunk.generation_info:
                session_id = chunk.generation_info["headers"].get("x-session-id") or chunk.generation_info[
                    "headers"
                ].get("X-Session-ID")
                if session_id:
                    self._session_id = session_id
                is_first_chunk = False
            yield chunk

    def reset_session(self) -> None:
        """
        Reset the session ID, starting a new conversation context.

        Call this method when you want to start a fresh conversation without
        carrying over context from previous requests.

        Example:
            ```python
            llm = LangGraphChatSequrityAI(...)
            llm.invoke([{"role": "user", "content": "Hello"}])
            llm.reset_session()  # Start fresh conversation
            llm.invoke([{"role": "user", "content": "Hello"}])
            ```
        """
        self._session_id = None

    @property
    def session_id(self) -> str | None:
        """Get the current session ID, if any."""
        return self._session_id

    def set_session_id(self, session_id: str | None) -> None:
        """
        Manually set the session ID.

        Use this to resume a previous conversation or share sessions across clients.

        Args:
            session_id: Session ID to use, or None to clear

        Example:
            ```python
            llm = LangGraphChatSequrityAI(...)
            llm.set_session_id("existing-session-id")
            llm.invoke([{"role": "user", "content": "Continue"}])  # Uses existing session
            ```
        """
        self._session_id = session_id


def create_sequrity_langgraph_client(
    sequrity_api_key: str,
    features: FeaturesHeader | None = None,
    security_policy: SecurityPolicyHeader | None = None,
    fine_grained_config: FineGrainedConfigHeader | None = None,
    service_provider: LlmServiceProvider | LlmServiceProviderStr = LlmServiceProvider.OPENROUTER,
    llm_api_key: str | None = None,
    base_url: str | None = None,
    endpoint_type: EndpointType | str = EndpointType.CHAT,
    model: str = "gpt-4",
    **kwargs: Any,
) -> LangGraphChatSequrityAI:
    """
    Create a ChatOpenAI-compatible client with Sequrity security features for LangGraph.

    This is a convenience factory function that creates a LangGraphChatSequrityAI instance
    configured to route requests through Sequrity's secure orchestrator.

    Args:
        sequrity_api_key: Sequrity API key (required)
        features: Security features configuration (LLM mode, taggers, etc.)
        security_policy: Security policy configuration (SQRT/Cedar policies)
        fine_grained_config: Fine-grained session configuration
        service_provider: LLM service provider (openai, openrouter, anthropic)
        llm_api_key: Optional API key for the LLM provider
        base_url: Sequrity base URL (default: https://api.sequrity.ai)
        endpoint_type: Endpoint type (chat, code, lang-graph). Defaults to chat.
        model: Model name to use (default: gpt-4)
        **kwargs: Additional arguments passed to ChatOpenAI

    Returns:
        Configured LangGraphChatSequrityAI client instance

    Example:
        ```python
        from sequrity.control.integrations.langgraph import create_sequrity_langgraph_client
        from sequrity.control import FeaturesHeader

        # Basic usage with dual-LLM
        llm = create_sequrity_langgraph_client(
            sequrity_api_key="your-key",
            features=FeaturesHeader.dual_llm()
        )

        # With security policy
        from sequrity.control import SecurityPolicyHeader
        llm = create_sequrity_langgraph_client(
            sequrity_api_key="your-key",
            features=FeaturesHeader.dual_llm(),
            security_policy=SecurityPolicyHeader.dual_llm()
        )

        # Use with LangChain
        response = llm.invoke([{"role": "user", "content": "Hello!"}])

        # Use with LangGraph
        from langgraph.graph import StateGraph
        from langgraph.prebuilt import ToolNode
        llm_with_tools = llm.bind_tools([...])
        # ... build your graph
        ```
    """
    return LangGraphChatSequrityAI(
        sequrity_api_key=sequrity_api_key,
        features=features,
        security_policy=security_policy,
        fine_grained_config=fine_grained_config,
        service_provider=service_provider,
        llm_api_key=llm_api_key,
        base_url=base_url,
        endpoint_type=endpoint_type,
        model=model,
        **kwargs,
    )
