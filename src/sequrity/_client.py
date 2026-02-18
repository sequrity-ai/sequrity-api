"""Sequrity API client classes."""

from __future__ import annotations

import os
from typing import Any

import httpx

from ._config import ClientConfig
from ._constants import SEQURITY_API_URL
from ._transport import AsyncTransport, SyncTransport
from .resources.chat import AsyncChatResource, ChatResource
from .resources.langgraph import LangGraphResource
from .resources.messages import AsyncMessagesResource, MessagesResource
from .resources.policy import AsyncPolicyResource, PolicyResource
from .types.enums import EndpointType
from .types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


class SequrityClient:
    """Synchronous client for the Sequrity API.

    Holds default configuration (API key, provider, security features, etc.)
    and exposes typed resource namespaces for each API surface.

    Example:
        ```python
        from sequrity import SequrityClient, FeaturesHeader, SecurityPolicyHeader

        client = SequrityClient(
            api_key="sq-xxx",
            llm_api_key="sk-xxx",
            provider="openrouter",
            features=FeaturesHeader.dual_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
        )

        response = client.chat.create(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gpt-5-mini",
        )
        ```
    """

    def __init__(
        self,
        api_key: str,
        *,
        llm_api_key: str | None = None,
        provider: str | None = None,
        features: FeaturesHeader | None = None,
        security_policy: SecurityPolicyHeader | None = None,
        fine_grained_config: FineGrainedConfigHeader | None = None,
        endpoint_type: EndpointType | str = EndpointType.CHAT,
        base_url: str | None = None,
        timeout: int = 300,
    ):
        """Initialize the Sequrity client.

        Args:
            api_key: Your Sequrity API key for authentication.
            llm_api_key: Default LLM provider API key.
            provider: Default LLM service provider slug (e.g., ``"openrouter"``).
            features: Default security features configuration.
            security_policy: Default security policy configuration.
            fine_grained_config: Default fine-grained configuration.
            endpoint_type: Default endpoint type. Defaults to ``"chat"``.
            base_url: Sequrity API base URL. Defaults to the ``SEQURITY_API_URL``
                environment variable, or ``https://api.sequrity.ai``.
            timeout: Default request timeout in seconds. Defaults to 300.
        """
        resolved_base_url = base_url or os.environ.get("SEQURITY_API_URL") or SEQURITY_API_URL
        config = ClientConfig(
            api_key=api_key,
            base_url=resolved_base_url,
            llm_api_key=llm_api_key,
            provider=provider,
            endpoint_type=str(endpoint_type),
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
        )
        self._http_client = httpx.Client(timeout=timeout)
        self._transport = SyncTransport(self._http_client, config)

        self.chat = ChatResource(self._transport)
        """OpenAI-compatible chat completions."""

        self.messages = MessagesResource(self._transport)
        """Anthropic Messages API."""

        self.policy = PolicyResource(self._transport)
        """Policy generation."""

        self.langgraph = LangGraphResource(self._transport)
        """LangGraph execution."""

    # -- Session management --------------------------------------------------

    @property
    def session_id(self) -> str | None:
        """Current auto-tracked session ID, or ``None``."""
        return self._transport._session_id

    def set_session_id(self, session_id: str | None) -> None:
        """Manually set the session ID for conversation continuity."""
        self._transport._session_id = session_id

    def reset_session(self) -> None:
        """Clear the session ID, starting a new conversation."""
        self._transport._session_id = None

    # -- Integration factories -----------------------------------------------

    def to_openai_agents_provider(self, **overrides: Any) -> Any:
        """Create an OpenAI Agents SDK ``ModelProvider`` from this client's config.

        Keyword arguments override the corresponding client defaults
        (e.g., ``service_provider``, ``llm_api_key``).

        Returns:
            A ``SequrityModelProvider`` instance.
        """
        from .integrations.openai_agents_sdk import create_sequrity_openai_agents_sdk_client

        cfg = self._transport._config
        return create_sequrity_openai_agents_sdk_client(
            sequrity_api_key=cfg.api_key,
            features=overrides.pop("features", cfg.features),
            security_policy=overrides.pop("security_policy", cfg.security_policy),
            fine_grained_config=overrides.pop("fine_grained_config", cfg.fine_grained_config),
            service_provider=overrides.pop("service_provider", cfg.provider or "openrouter"),
            llm_api_key=overrides.pop("llm_api_key", cfg.llm_api_key),
            base_url=overrides.pop("base_url", cfg.base_url),
            endpoint_type=overrides.pop("endpoint_type", cfg.endpoint_type),
            **overrides,
        )

    def to_langgraph_client(self, model: str = "gpt-4", **overrides: Any) -> Any:
        """Create a LangChain ``ChatOpenAI`` client from this client's config.

        Args:
            model: Model name for the LangChain client.

        Keyword arguments override the corresponding client defaults.

        Returns:
            A ``LangGraphChatSequrityAI`` instance.
        """
        from .integrations.langgraph import create_sequrity_langgraph_client

        cfg = self._transport._config
        return create_sequrity_langgraph_client(
            sequrity_api_key=cfg.api_key,
            features=overrides.pop("features", cfg.features),
            security_policy=overrides.pop("security_policy", cfg.security_policy),
            fine_grained_config=overrides.pop("fine_grained_config", cfg.fine_grained_config),
            service_provider=overrides.pop("service_provider", cfg.provider or "openrouter"),
            llm_api_key=overrides.pop("llm_api_key", cfg.llm_api_key),
            base_url=overrides.pop("base_url", cfg.base_url),
            endpoint_type=overrides.pop("endpoint_type", cfg.endpoint_type),
            model=model,
            **overrides,
        )

    # -- Lifecycle -----------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http_client.close()

    def __enter__(self) -> SequrityClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncSequrityClient:
    """Asynchronous client for the Sequrity API.

    Same API as :class:`SequrityClient` but with async resource methods.

    Example:
        ```python
        async with AsyncSequrityClient(api_key="sq-xxx") as client:
            response = await client.chat.create(
                messages=[{"role": "user", "content": "Hello!"}],
                model="gpt-5-mini",
            )
        ```
    """

    def __init__(
        self,
        api_key: str,
        *,
        llm_api_key: str | None = None,
        provider: str | None = None,
        features: FeaturesHeader | None = None,
        security_policy: SecurityPolicyHeader | None = None,
        fine_grained_config: FineGrainedConfigHeader | None = None,
        endpoint_type: EndpointType | str = EndpointType.CHAT,
        base_url: str | None = None,
        timeout: int = 300,
    ):
        resolved_base_url = base_url or os.environ.get("SEQURITY_API_URL") or SEQURITY_API_URL
        config = ClientConfig(
            api_key=api_key,
            base_url=resolved_base_url,
            llm_api_key=llm_api_key,
            provider=provider,
            endpoint_type=str(endpoint_type),
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
        )
        self._http_client = httpx.AsyncClient(timeout=timeout)
        self._transport = AsyncTransport(self._http_client, config)

        self.chat = AsyncChatResource(self._transport)
        self.messages = AsyncMessagesResource(self._transport)
        self.policy = AsyncPolicyResource(self._transport)

    # -- Session management --------------------------------------------------

    @property
    def session_id(self) -> str | None:
        return self._transport._session_id

    def set_session_id(self, session_id: str | None) -> None:
        self._transport._session_id = session_id

    def reset_session(self) -> None:
        self._transport._session_id = None

    # -- Lifecycle -----------------------------------------------------------

    async def close(self) -> None:
        await self._http_client.aclose()

    async def __aenter__(self) -> AsyncSequrityClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
