"""Sequrity Control client classes."""

from __future__ import annotations

from typing import Any

import httpx

from ._config import ControlConfig
from ._transport import ControlAsyncTransport, ControlSyncTransport
from .resources.annotations import AnnotationsResource, AsyncAnnotationsResource
from .resources.chat import AsyncChatResource, ChatResource
from .resources.langgraph import LangGraphResource
from .resources.messages import AsyncMessagesResource, MessagesResource
from .resources.policy import AsyncPolicyResource, PolicyResource


class ControlClient:
    """Synchronous client namespace for the Sequrity Control product.

    Holds Control-specific configuration and exposes typed resource namespaces.

    Example:
        ```python
        from sequrity import SequrityClient
        from sequrity.control import ControlConfig, FeaturesHeader

        client = SequrityClient(
            api_key="sq-xxx",
            control=ControlConfig(
                features=FeaturesHeader.dual_llm(),
            ),
        )

        response = client.control.chat.create(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gpt-5-mini",
        )
        ```
    """

    def __init__(
        self,
        http_client: httpx.Client,
        api_key: str,
        base_url: str,
        config: ControlConfig | None = None,
    ):
        config = config or ControlConfig()
        self._transport = ControlSyncTransport(http_client, api_key, base_url, config)

        self.chat = ChatResource(self._transport)
        """OpenAI-compatible chat completions."""

        self.messages = MessagesResource(self._transport)
        """Anthropic Messages API."""

        self.policy = PolicyResource(self._transport)
        """Policy generation."""

        self.langgraph = LangGraphResource(self._transport)
        """LangGraph execution."""

        self.annotations = AnnotationsResource(self._transport)
        """Session-log annotations."""

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
            sequrity_api_key=self._transport._api_key,
            features=overrides.pop("features", cfg.features),
            security_policy=overrides.pop("security_policy", cfg.security_policy),
            fine_grained_config=overrides.pop("fine_grained_config", cfg.fine_grained_config),
            service_provider=overrides.pop("service_provider", cfg.provider or "openrouter"),
            llm_api_key=overrides.pop("llm_api_key", cfg.llm_api_key),
            base_url=overrides.pop("base_url", self._transport._base_url),
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
            sequrity_api_key=self._transport._api_key,
            features=overrides.pop("features", cfg.features),
            security_policy=overrides.pop("security_policy", cfg.security_policy),
            fine_grained_config=overrides.pop("fine_grained_config", cfg.fine_grained_config),
            service_provider=overrides.pop("service_provider", cfg.provider or "openrouter"),
            llm_api_key=overrides.pop("llm_api_key", cfg.llm_api_key),
            base_url=overrides.pop("base_url", self._transport._base_url),
            endpoint_type=overrides.pop("endpoint_type", cfg.endpoint_type),
            model=model,
            **overrides,
        )


class AsyncControlClient:
    """Asynchronous client namespace for the Sequrity Control product.

    Same API as :class:`ControlClient` but with async resource methods.

    Example:
        ```python
        async with AsyncSequrityClient(api_key="sq-xxx") as client:
            response = await client.control.chat.create(
                messages=[{"role": "user", "content": "Hello!"}],
                model="gpt-5-mini",
            )
        ```
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_key: str,
        base_url: str,
        config: ControlConfig | None = None,
    ):
        config = config or ControlConfig()
        self._transport = ControlAsyncTransport(http_client, api_key, base_url, config)

        self.chat = AsyncChatResource(self._transport)
        self.messages = AsyncMessagesResource(self._transport)
        self.policy = AsyncPolicyResource(self._transport)
        self.annotations = AsyncAnnotationsResource(self._transport)

    # -- Session management --------------------------------------------------

    @property
    def session_id(self) -> str | None:
        return self._transport._session_id

    def set_session_id(self, session_id: str | None) -> None:
        self._transport._session_id = session_id

    def reset_session(self) -> None:
        self._transport._session_id = None
