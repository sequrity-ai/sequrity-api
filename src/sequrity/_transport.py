"""Unified HTTP transport layer with config defaults, session tracking, and error handling."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import httpx

from ._config import ClientConfig
from ._constants import build_control_url, build_policy_gen_url, build_sequrity_headers
from ._exceptions import SequrityAPIError, SequrityConnectionError
from ._sentinel import NOT_GIVEN, _NotGiven
from .types.enums import RestApiType

if TYPE_CHECKING:
    from .types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader

_T = TypeVar("_T")


def _resolve(override: _T | _NotGiven, default: _T) -> _T:
    """Return *override* unless it is ``NOT_GIVEN``, in which case return *default*."""
    if isinstance(override, _NotGiven):
        return default
    return override


class SyncTransport:
    """Synchronous HTTP transport for the Sequrity API.

    Handles URL building, header construction, session tracking, and error
    handling so that resource classes remain thin.
    """

    def __init__(self, http_client: httpx.Client, config: ClientConfig):
        self._http = http_client
        self._config = config
        self._session_id: str | None = None

    # -- URL building --------------------------------------------------------

    def build_url(
        self,
        rest_api_type: RestApiType,
        *,
        provider: str | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
    ) -> str:
        """Build a standard ``/control/...`` URL, merging with config defaults."""
        p = _resolve(provider, self._config.provider)
        et = _resolve(endpoint_type, self._config.endpoint_type)
        return build_control_url(self._config.base_url, et, rest_api_type, p)

    def build_policy_gen_url(self, request_type: str) -> str:
        """Build the policy generation endpoint URL for the given request type."""
        return build_policy_gen_url(self._config.base_url, request_type)

    # -- Request execution ---------------------------------------------------

    def request(
        self,
        *,
        url: str,
        payload: dict,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        include_session: bool = True,
    ) -> httpx.Response:
        """POST *payload* as JSON to *url* with merged Sequrity headers.

        Args:
            url: Fully-qualified endpoint URL.
            payload: JSON-serializable request body.
            llm_api_key: LLM provider key override (``NOT_GIVEN`` → config default).
            features: ``FeaturesHeader`` override (``NOT_GIVEN`` → config default).
            security_policy: ``SecurityPolicyHeader`` override.
            fine_grained_config: ``FineGrainedConfigHeader`` override.
            session_id: Explicit session ID override. ``NOT_GIVEN`` uses the
                auto-tracked session ID.
            include_session: Whether to include session-related headers. Set to
                ``False`` for endpoints like policy generation that don't use sessions.

        Returns:
            The raw ``httpx.Response`` (status already validated).

        Raises:
            SequrityAPIError: On HTTP 4xx/5xx responses.
            SequrityConnectionError: On network failures.
        """
        eff_llm_key = _resolve(llm_api_key, self._config.llm_api_key)
        eff_features = _resolve(features, self._config.features)
        eff_policy = _resolve(security_policy, self._config.security_policy)
        eff_config = _resolve(fine_grained_config, self._config.fine_grained_config)

        if include_session:
            eff_session = _resolve(session_id, self._session_id)
        else:
            eff_session = None

        headers = build_sequrity_headers(
            api_key=self._config.api_key,
            llm_api_key=eff_llm_key,
            features=eff_features.dump_for_headers(mode="json_str") if eff_features else None,
            policy=eff_policy.dump_for_headers(mode="json_str") if eff_policy else None,
            config=eff_config.dump_for_headers(mode="json_str") if eff_config else None,
            session_id=eff_session,
        )

        try:
            response = self._http.post(url, json=payload, headers=headers)
        except httpx.ConnectError as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        # Auto-track session ID from response
        if include_session:
            new_session = response.headers.get("X-Session-ID")
            if new_session:
                self._session_id = new_session

        return response


class AsyncTransport:
    """Asynchronous HTTP transport for the Sequrity API.

    Mirror of :class:`SyncTransport` using ``httpx.AsyncClient``.
    """

    def __init__(self, http_client: httpx.AsyncClient, config: ClientConfig):
        self._http = http_client
        self._config = config
        self._session_id: str | None = None

    def build_url(
        self,
        rest_api_type: RestApiType,
        *,
        provider: str | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
    ) -> str:
        p = _resolve(provider, self._config.provider)
        et = _resolve(endpoint_type, self._config.endpoint_type)
        return build_control_url(self._config.base_url, et, rest_api_type, p)

    def build_policy_gen_url(self, request_type: str) -> str:
        return build_policy_gen_url(self._config.base_url, request_type)

    async def request(
        self,
        *,
        url: str,
        payload: dict,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        include_session: bool = True,
    ) -> httpx.Response:
        """Async variant of :meth:`SyncTransport.request`."""
        eff_llm_key = _resolve(llm_api_key, self._config.llm_api_key)
        eff_features = _resolve(features, self._config.features)
        eff_policy = _resolve(security_policy, self._config.security_policy)
        eff_config = _resolve(fine_grained_config, self._config.fine_grained_config)

        if include_session:
            eff_session = _resolve(session_id, self._session_id)
        else:
            eff_session = None

        headers = build_sequrity_headers(
            api_key=self._config.api_key,
            llm_api_key=eff_llm_key,
            features=eff_features.dump_for_headers(mode="json_str") if eff_features else None,
            policy=eff_policy.dump_for_headers(mode="json_str") if eff_policy else None,
            config=eff_config.dump_for_headers(mode="json_str") if eff_config else None,
            session_id=eff_session,
        )

        try:
            response = await self._http.post(url, json=payload, headers=headers)
        except httpx.ConnectError as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        if include_session:
            new_session = response.headers.get("X-Session-ID")
            if new_session:
                self._session_id = new_session

        return response
