"""Sequrity API client classes."""

from __future__ import annotations

import os

import httpx

from .control._client import AsyncControlClient, ControlClient
from .control._config import ControlConfig
from .control._constants import SEQURITY_BASE_URL


class SequrityClient:
    """Synchronous client for the Sequrity API.

    Thin orchestrator that owns the HTTP connection pool and delegates to
    product-specific namespaces.

    Example:
        ```python
        from sequrity import SequrityClient
        from sequrity.control import ControlConfig, FeaturesHeader, SecurityPolicyHeader

        client = SequrityClient(
            api_key="sq-xxx",
            control=ControlConfig(
                llm_api_key="sk-xxx",
                provider="openrouter",
                features=FeaturesHeader.dual_llm(),
                security_policy=SecurityPolicyHeader.dual_llm(),
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
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: int = 300,
        control: ControlConfig | None = None,
    ):
        """Initialize the Sequrity client.

        Args:
            api_key: Your Sequrity API key for authentication.
            base_url: Sequrity API base URL. Defaults to the ``SEQURITY_BASE_URL``
                environment variable, or ``https://api.sequrity.ai``.
            timeout: Default request timeout in seconds. Defaults to 300.
            control: Configuration for the Sequrity Control product. When omitted,
                an empty ``ControlConfig`` is used (all defaults are None, configure
                per-request instead).
        """
        self._api_key = api_key
        self._base_url = base_url or os.environ.get("SEQURITY_BASE_URL") or SEQURITY_BASE_URL
        self._http_client = httpx.Client(timeout=timeout)

        self.control = ControlClient(
            self._http_client,
            self._api_key,
            self._base_url,
            config=control,
        )
        """Sequrity Control product namespace."""

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
            response = await client.control.chat.create(
                messages=[{"role": "user", "content": "Hello!"}],
                model="gpt-5-mini",
            )
        ```
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: int = 300,
        control: ControlConfig | None = None,
    ):
        self._api_key = api_key
        self._base_url = base_url or os.environ.get("SEQURITY_BASE_URL") or SEQURITY_BASE_URL
        self._http_client = httpx.AsyncClient(timeout=timeout)

        self.control = AsyncControlClient(
            self._http_client,
            self._api_key,
            self._base_url,
            config=control,
        )

    # -- Lifecycle -----------------------------------------------------------

    async def close(self) -> None:
        await self._http_client.aclose()

    async def __aenter__(self) -> AsyncSequrityClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
