"""
OpenAI Agent ADK integration for Sequrity Control.

This module provides an AsyncOpenAI-compatible client that routes requests through
Sequrity's secure orchestrator with automatic session management and security features.

Example:
    ```python
    from sequrity.control.integrations.openai_agents_sdk import create_sequrity_openai_agents_sdk_client
    from sequrity.control import FeaturesHeader, SecurityPolicyHeader
    from agents import Agent, Runner, RunConfig

    # Create client with Sequrity security features
    provider = create_sequrity_openai_agents_sdk_client(
        sequrity_api_key="your-sequrity-key",
        features=FeaturesHeader.dual_llm(),
        security_policy=SecurityPolicyHeader.dual_llm()
    )

    # Use with OpenAI Agents SDK
    agent = Agent(name="Assistant", instructions="You are helpful.")
    config = RunConfig(model="gpt-5-mini", model_provider=provider)
    result = await Runner.run(agent, input="Hello!", run_config=config)
    ```
"""

import os
from typing import Any, AsyncIterator

import httpx

# Import Agents SDK types for runtime
from agents.agent_output import AgentOutputSchemaBase
from agents.handoffs import Handoff
from agents.items import ModelResponse, TResponseInputItem, TResponseStreamEvent
from agents.model_settings import ModelSettings
from agents.models.interface import Model, ModelProvider, ModelTracing
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from agents.tool import Tool
from openai import AsyncOpenAI
from openai.types.responses.response_prompt_param import ResponsePromptParam

from .._constants import SEQURITY_BASE_URL, build_control_base_url, build_sequrity_headers
from ..types.enums import EndpointType
from ..types.headers import (
    FeaturesHeader,
    FineGrainedConfigHeader,
    SecurityPolicyHeader,
)


class SequrityAsyncOpenAI(AsyncOpenAI):
    """
    AsyncOpenAI client configured to route requests through Sequrity's secure orchestrator.

    This client is a drop-in replacement for AsyncOpenAI that automatically:
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
        timeout: Request timeout in seconds (default: 60.0)
        **kwargs: Additional arguments passed to AsyncOpenAI

    Example:
        ```python
        features = FeaturesHeader.dual_llm()

        client = SequrityAsyncOpenAI(
            sequrity_api_key="your-key",
            features=features,
        )

        # Session ID is automatically tracked
        response1 = await client.chat.completions.create(...)
        response2 = await client.chat.completions.create(...)  # Uses same session
        ```
    """

    def __init__(
        self,
        sequrity_api_key: str,
        features: FeaturesHeader | None = None,
        security_policy: SecurityPolicyHeader | None = None,
        fine_grained_config: FineGrainedConfigHeader | None = None,
        service_provider: str = "openrouter",
        llm_api_key: str | None = None,
        base_url: str | None = None,
        endpoint_type: EndpointType | str = EndpointType.CHAT,
        timeout: float = 60.0,
        **kwargs: Any,
    ):
        """Initialize Sequrity-enabled AsyncOpenAI client."""
        if base_url is None:
            base_url = os.getenv("SEQURITY_BASE_URL", SEQURITY_BASE_URL)

        # Store Sequrity-specific configuration
        self._sequrity_features = features
        self._sequrity_policy = security_policy
        self._sequrity_config = fine_grained_config
        self._session_id: str | None = None

        # Build headers using shared builder
        default_headers = build_sequrity_headers(
            api_key=sequrity_api_key,
            llm_api_key=llm_api_key,
            features=features.dump_for_headers(mode="json_str") if features else None,
            policy=security_policy.dump_for_headers(mode="json_str") if security_policy else None,
            config=fine_grained_config.dump_for_headers(mode="json_str") if fine_grained_config else None,
        )

        # Merge with any user-provided headers
        if "default_headers" in kwargs:
            default_headers.update(kwargs.pop("default_headers"))

        # Construct Sequrity API endpoint URL
        sequrity_base_url = build_control_base_url(base_url, endpoint_type, service_provider)

        # Initialize parent AsyncOpenAI with Sequrity configuration
        super().__init__(
            api_key=sequrity_api_key,
            base_url=sequrity_base_url,
            timeout=timeout,
            default_headers=default_headers,
            **kwargs,
        )

        # Set up response hook to capture session IDs
        self._setup_session_tracking()

    def _setup_session_tracking(self) -> None:
        """Set up httpx event hooks to capture and inject session IDs."""

        async def capture_session_id(response: httpx.Response) -> None:
            """Extract session ID from response headers."""
            session_id = response.headers.get("x-session-id") or response.headers.get("X-Session-ID")
            if session_id and not self._session_id:
                self._session_id = session_id

        async def inject_session_id(request: httpx.Request) -> None:
            """Inject session ID into request headers if available."""
            if self._session_id:
                request.headers["X-Session-ID"] = self._session_id

        # Access the underlying httpx client
        if hasattr(self, "_client") and isinstance(self._client, httpx.AsyncClient):
            # Set up event hooks
            if not hasattr(self._client, "event_hooks"):
                self._client.event_hooks = {}

            # Add request hook for session injection
            if "request" not in self._client.event_hooks:
                self._client.event_hooks["request"] = []
            self._client.event_hooks["request"].append(inject_session_id)

            # Add response hook for session capture
            if "response" not in self._client.event_hooks:
                self._client.event_hooks["response"] = []
            self._client.event_hooks["response"].append(capture_session_id)

    def reset_session(self) -> None:
        """
        Reset the session ID, starting a new conversation context.

        Call this method when you want to start a fresh conversation without
        carrying over context from previous requests.

        Example:
            ```python
            client = SequrityAsyncOpenAI(...)
            await client.chat.completions.create(...)
            client.reset_session()  # Start fresh conversation
            await client.chat.completions.create(...)
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
            client = SequrityAsyncOpenAI(...)
            client.set_session_id("existing-session-id")
            await client.chat.completions.create(...)  # Uses existing session
            ```
        """
        self._session_id = session_id


class SequrityModel(Model):
    """
    A Model wrapper that tracks session IDs across requests for Sequrity.

    Sequrity requires maintaining the same X-Session-ID header across all turns
    of a conversation to properly track state in the dual-LLM architecture.
    """

    def __init__(self, base_model: OpenAIChatCompletionsModel, openai_client: SequrityAsyncOpenAI):
        self.base_model = base_model
        self.openai_client = openai_client

    async def get_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
        *,
        previous_response_id: str | None,
        conversation_id: str | None,
        prompt: ResponsePromptParam | None,
    ) -> ModelResponse:
        # Reset session ID for each Runner.run() call
        # This ensures each agent execution starts fresh
        self.openai_client.reset_session()

        # Delegate to base model - session tracking is handled by SequrityAsyncOpenAI's httpx hooks
        response = await self.base_model.get_response(
            system_instructions,
            input,
            model_settings,
            tools,
            output_schema,
            handoffs,
            tracing,
            previous_response_id=previous_response_id,
            conversation_id=conversation_id,
            prompt=prompt,
        )

        return response

    async def stream_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
        *,
        previous_response_id: str | None,
        conversation_id: str | None,
        prompt: ResponsePromptParam | None,
    ) -> AsyncIterator[TResponseStreamEvent]:
        # Reset session ID for each Runner.run() call
        # This ensures each agent execution starts fresh
        self.openai_client.reset_session()

        # Delegate to base model - session tracking is handled by SequrityAsyncOpenAI's httpx hooks
        async for event in self.base_model.stream_response(
            system_instructions,
            input,
            model_settings,
            tools,
            output_schema,
            handoffs,
            tracing,
            previous_response_id=previous_response_id,
            conversation_id=conversation_id,
            prompt=prompt,
        ):
            yield event


class SequrityModelProvider(ModelProvider):
    """
    ModelProvider implementation for Sequrity's dual-LLM architecture.

    This provider wraps the SequrityAsyncOpenAI client and implements the
    ModelProvider interface required by the OpenAI Agents SDK. It also exposes
    the underlying AsyncOpenAI client interface for direct API access.

    Args:
        openai_client: SequrityAsyncOpenAI client configured with Sequrity settings

    Example:
        ```python
        # Use as a ModelProvider with Agents SDK
        provider = SequrityModelProvider(SequrityAsyncOpenAI(sequrity_api_key="your-key"))
        config = RunConfig(model="gpt-5-mini", model_provider=provider)
        result = await Runner.run(agent, input="Hello", run_config=config)

        # Or use directly as an AsyncOpenAI client
        response = await provider.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": "Hello"}]
        )
        ```
    """

    def __init__(self, openai_client: SequrityAsyncOpenAI):
        self.openai_client = openai_client
        self._model_cache: dict[str, SequrityModel] = {}

    def get_model(self, model_name: str | None) -> Model:
        """
        Get a model configured to use Sequrity's endpoint.

        Args:
            model_name: The name of the model to use (e.g., "gpt-4", "gpt-5-mini")

        Returns:
            A Model instance configured for Sequrity with session tracking
        """
        if model_name is None:
            model_name = "gpt-5-mini"  # Default model

        # Return cached model if it exists (to maintain session state)
        if model_name in self._model_cache:
            return self._model_cache[model_name]

        # Create base OpenAI model
        base_model = OpenAIChatCompletionsModel(
            model=model_name,
            openai_client=self.openai_client,
        )

        # Wrap with session tracking and cache it
        sequrity_model = SequrityModel(base_model, self.openai_client)
        self._model_cache[model_name] = sequrity_model
        return sequrity_model

    # Expose AsyncOpenAI interface by delegating to the underlying client
    @property
    def chat(self):
        """Access to chat completions API."""
        return self.openai_client.chat

    @property
    def session_id(self) -> str | None:
        """Get the current session ID."""
        return self.openai_client.session_id

    def set_session_id(self, session_id: str | None) -> None:
        """Set the session ID."""
        self.openai_client.set_session_id(session_id)

    def reset_session(self) -> None:
        """Reset the session ID."""
        self.openai_client.reset_session()


def create_sequrity_openai_agents_sdk_client(
    sequrity_api_key: str,
    features: FeaturesHeader | None = None,
    security_policy: SecurityPolicyHeader | None = None,
    fine_grained_config: FineGrainedConfigHeader | None = None,
    service_provider: str = "openrouter",
    llm_api_key: str | None = None,
    base_url: str | None = None,
    endpoint_type: EndpointType | str = EndpointType.CHAT,
    timeout: float = 60.0,
    **kwargs: Any,
) -> SequrityModelProvider:
    """
    Create a ModelProvider for use with OpenAI Agents SDK and Sequrity.

    This factory function creates a SequrityModelProvider that wraps a
    SequrityAsyncOpenAI client, providing the ModelProvider interface
    required by the OpenAI Agents SDK's RunConfig.

    Args:
        sequrity_api_key: Sequrity API key (required)
        features: Security features configuration (LLM mode, taggers, etc.)
        security_policy: Security policy configuration (SQRT/Cedar policies)
        fine_grained_config: Fine-grained session configuration
        service_provider: LLM service provider (openai, openrouter, anthropic)
        llm_api_key: Optional API key for the LLM provider
        base_url: Sequrity base URL (default: https://api.sequrity.ai)
        endpoint_type: Endpoint type (chat, code, lang-graph). Defaults to chat.
        timeout: Request timeout in seconds (default: 60.0)
        **kwargs: Additional arguments passed to AsyncOpenAI

    Returns:
        Configured SequrityModelProvider instance

    Example:
        ```python
        from sequrity.control.integrations.openai_agents_sdk import create_sequrity_openai_agents_sdk_client
        from sequrity.control import FeaturesHeader
        from agents import Agent, Runner, RunConfig

        # Create provider with dual-LLM
        provider = create_sequrity_openai_agents_sdk_client(
            sequrity_api_key="your-key",
            features=FeaturesHeader.dual_llm()
        )

        # Use with OpenAI Agents SDK
        agent = Agent(name="Assistant", instructions="You are helpful.")
        config = RunConfig(model="gpt-5-mini", model_provider=provider)
        result = await Runner.run(agent, input="Hello", run_config=config)
        ```
    """
    # Create the AsyncOpenAI client with Sequrity configuration
    client = SequrityAsyncOpenAI(
        sequrity_api_key=sequrity_api_key,
        features=features,
        security_policy=security_policy,
        fine_grained_config=fine_grained_config,
        service_provider=service_provider,
        llm_api_key=llm_api_key,
        base_url=base_url,
        endpoint_type=endpoint_type,
        timeout=timeout,
        **kwargs,
    )

    # Wrap in ModelProvider for Agents SDK compatibility
    return SequrityModelProvider(client)
