"""
OpenAI Agent ADK integration for Sequrity.

This module provides an AsyncOpenAI-compatible client that routes requests through
Sequrity's secure orchestrator with automatic session management and security features.

Example:
    ```python
    from sequrity_api.integrations.openai_adk import create_sequrity_openai_client
    from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader

    # Create client with Sequrity security features
    client = create_sequrity_openai_client(
        sequrity_api_key="your-sequrity-key",
        features=FeaturesHeader.create_dual_llm_headers(),
        security_policy=SecurityPolicyHeader.create_default()
    )

    # Use with OpenAI Agent ADK
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    ```
"""

from typing import Any

import httpx
from openai import AsyncOpenAI

from ..types.control.headers import (
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
        service_provider: LLM service provider (openai, openrouter, azurecredits)
        llm_api_key: Optional API key for the LLM provider
        base_url: Sequrity base URL (default: https://api.sequrity.ai)
        timeout: Request timeout in seconds (default: 60.0)
        **kwargs: Additional arguments passed to AsyncOpenAI

    Example:
        ```python
        features = FeaturesHeader.create_dual_llm_headers()
        policy = SecurityPolicyHeader.create_default()

        client = SequrityAsyncOpenAI(
            sequrity_api_key="your-key",
            features=features,
            security_policy=policy
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
        base_url: str = "https://api.sequrity.ai",
        timeout: float = 60.0,
        **kwargs: Any,
    ):
        """Initialize Sequrity-enabled AsyncOpenAI client."""
        # Store Sequrity-specific configuration
        self._sequrity_features = features
        self._sequrity_policy = security_policy
        self._sequrity_config = fine_grained_config
        self._session_id: str | None = None

        # Build headers for Sequrity
        default_headers: dict[str, str] = {}

        # Add LLM provider API key if provided
        if llm_api_key:
            default_headers["X-Api-Key"] = llm_api_key

        # Add security headers if configured
        if features:
            features_header = features.dump_for_headers(mode="json_str")
            if isinstance(features_header, str):
                default_headers["X-Security-Features"] = features_header

        if security_policy:
            policy_header = security_policy.dump_for_headers(mode="json_str")
            if isinstance(policy_header, str):
                default_headers["X-Security-Policy"] = policy_header

        if fine_grained_config:
            config_header = fine_grained_config.dump_for_headers(mode="json_str")
            if isinstance(config_header, str):
                default_headers["X-Security-Config"] = config_header

        # Merge with any user-provided headers
        if "default_headers" in kwargs:
            default_headers.update(kwargs.pop("default_headers"))

        # Construct Sequrity API endpoint URL
        sequrity_base_url = f"{base_url}/control/{service_provider}/v1"

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
            session_id = response.headers.get("x-session-id") or response.headers.get("X-Session-Id")
            if session_id and not self._session_id:
                self._session_id = session_id

        async def inject_session_id(request: httpx.Request) -> None:
            """Inject session ID into request headers if available."""
            if self._session_id:
                request.headers["X-Session-Id"] = self._session_id

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


def create_sequrity_openai_client(
    sequrity_api_key: str,
    features: FeaturesHeader | None = None,
    security_policy: SecurityPolicyHeader | None = None,
    fine_grained_config: FineGrainedConfigHeader | None = None,
    service_provider: str = "openrouter",
    llm_api_key: str | None = None,
    base_url: str = "https://api.sequrity.ai",
    timeout: float = 60.0,
    **kwargs: Any,
) -> SequrityAsyncOpenAI:
    """
    Create an AsyncOpenAI-compatible client with Sequrity security features.

    This is a convenience factory function that creates a SequrityAsyncOpenAI instance
    configured to route requests through Sequrity's secure orchestrator.

    Args:
        sequrity_api_key: Sequrity API key (required)
        features: Security features configuration (LLM mode, taggers, etc.)
        security_policy: Security policy configuration (SQRT/Cedar policies)
        fine_grained_config: Fine-grained session configuration
        service_provider: LLM service provider (openai, openrouter, azurecredits)
        llm_api_key: Optional API key for the LLM provider
        base_url: Sequrity base URL (default: https://api.sequrity.ai)
        timeout: Request timeout in seconds (default: 60.0)
        **kwargs: Additional arguments passed to AsyncOpenAI

    Returns:
        Configured SequrityAsyncOpenAI client instance

    Example:
        ```python
        from sequrity_api.integrations.openai_adk import create_sequrity_openai_client
        from sequrity_api.types.control.headers import FeaturesHeader

        # Basic usage with dual-LLM
        client = create_sequrity_openai_client(
            sequrity_api_key="your-key",
            features=FeaturesHeader.create_dual_llm_headers()
        )

        # With security policy
        from sequrity_api.types.control.headers import SecurityPolicyHeader
        client = create_sequrity_openai_client(
            sequrity_api_key="your-key",
            features=FeaturesHeader.create_dual_llm_headers(),
            security_policy=SecurityPolicyHeader.create_default()
        )

        # Use with OpenAI Agent ADK
        from agents import Agent, Runner, RunConfig
        config = RunConfig(model="gpt-4", model_provider=client)
        result = await Runner.run(agent, input="Hello", run_config=config)
        ```
    """
    return SequrityAsyncOpenAI(
        sequrity_api_key=sequrity_api_key,
        features=features,
        security_policy=security_policy,
        fine_grained_config=fine_grained_config,
        service_provider=service_provider,
        llm_api_key=llm_api_key,
        base_url=base_url,
        timeout=timeout,
        **kwargs,
    )
