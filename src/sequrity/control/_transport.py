"""HTTP transport layer for Sequrity Control with config defaults, session tracking, and error handling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import httpx

from .._exceptions import SequrityAPIError, SequrityConnectionError
from .._sentinel import NOT_GIVEN, _NotGiven
from ..types.enums import LlmServiceProvider, LlmServiceProviderStr, RestApiType
from ._config import ControlConfig
from ._constants import build_control_url, build_policy_gen_url, build_sequrity_headers

if TYPE_CHECKING:
    from .types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader

_T = TypeVar("_T")


def _resolve(override: _T | _NotGiven, default: _T) -> _T:
    """Return *override* unless it is ``NOT_GIVEN``, in which case return *default*."""
    if isinstance(override, _NotGiven):
        return default
    return override


class ControlSyncTransport:
    """Synchronous HTTP transport for the Sequrity Control API.

    Handles URL building, header construction, session tracking, and error
    handling so that resource classes remain thin.
    """

    def __init__(self, http_client: httpx.Client, api_key: str, base_url: str, config: ControlConfig):
        self._http = http_client
        self._api_key = api_key
        self._base_url = base_url
        self._config = config
        self._session_id: str | None = None

    # -- URL building --------------------------------------------------------

    def build_url(
        self,
        rest_api_type: RestApiType,
        *,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
    ) -> str:
        """Build a standard ``/control/...`` URL, merging with config defaults."""
        p = _resolve(provider, self._config.provider)
        et = _resolve(endpoint_type, self._config.endpoint_type)
        return build_control_url(self._base_url, et, rest_api_type, p)

    def build_policy_gen_url(self, request_type: str) -> str:
        """Build the policy generation endpoint URL for the given request type."""
        return build_policy_gen_url(self._base_url, request_type)

    # -- Header building (shared) --------------------------------------------

    def _build_headers(
        self,
        *,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        feature_overrides: dict[str, Any] | None = None,
        policy_overrides: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        eff_llm_key = _resolve(llm_api_key, self._config.llm_api_key)
        eff_features = _resolve(features, self._config.features)
        eff_policy = _resolve(security_policy, self._config.security_policy)
        eff_config = _resolve(fine_grained_config, self._config.fine_grained_config)
        eff_session = _resolve(session_id, None)

        features_str = (
            eff_features.dump_for_headers(mode="json_str", overrides=feature_overrides) if eff_features else None
        )
        policy_str = eff_policy.dump_for_headers(mode="json_str", overrides=policy_overrides) if eff_policy else None
        config_str = eff_config.dump_for_headers(mode="json_str", overrides=config_overrides) if eff_config else None

        headers = build_sequrity_headers(
            api_key=self._api_key,
            llm_api_key=eff_llm_key,
            features=features_str,
            policy=policy_str,
            config=config_str,
            session_id=eff_session,
        )
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _track_session(self, response: httpx.Response) -> None:
        new_session = response.headers.get("X-Session-ID")
        if new_session:
            self._session_id = new_session

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
        feature_overrides: dict[str, Any] | None = None,
        policy_overrides: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """POST *payload* as JSON to *url* with merged Sequrity headers.

        Returns:
            The raw ``httpx.Response`` (status already validated).

        Raises:
            SequrityAPIError: On HTTP 4xx/5xx responses.
            SequrityConnectionError: On network failures.
        """
        headers = self._build_headers(
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
            feature_overrides=feature_overrides,
            policy_overrides=policy_overrides,
            config_overrides=config_overrides,
            custom_headers=custom_headers,
        )

        try:
            response = self._http.post(url, json=payload, headers=headers)
        except httpx.ConnectError as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        self._track_session(response)
        return response

    def stream_request(
        self,
        *,
        url: str,
        payload: dict,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        feature_overrides: dict[str, Any] | None = None,
        policy_overrides: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Open a streaming POST request.

        Returns the raw ``httpx.Response`` in streaming mode. The caller
        is responsible for closing the response (typically via a
        :class:`SyncStream` wrapper).

        Raises:
            SequrityAPIError: On HTTP 4xx/5xx responses.
            SequrityConnectionError: On network failures.
        """
        headers = self._build_headers(
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
            feature_overrides=feature_overrides,
            policy_overrides=policy_overrides,
            config_overrides=config_overrides,
            custom_headers=custom_headers,
        )

        request = self._http.build_request("POST", url, json=payload, headers=headers)

        try:
            response = self._http.send(request, stream=True)
        except httpx.ConnectError as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            response.read()  # consume body for error message
            response.close()
            raise SequrityAPIError.from_response(response)

        self._track_session(response)
        return response


class ControlAsyncTransport:
    """Asynchronous HTTP transport for the Sequrity Control API.

    Mirror of :class:`ControlSyncTransport` using ``httpx.AsyncClient``.
    """

    def __init__(self, http_client: httpx.AsyncClient, api_key: str, base_url: str, config: ControlConfig):
        self._http = http_client
        self._api_key = api_key
        self._base_url = base_url
        self._config = config
        self._session_id: str | None = None

    def build_url(
        self,
        rest_api_type: RestApiType,
        *,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
    ) -> str:
        p = _resolve(provider, self._config.provider)
        et = _resolve(endpoint_type, self._config.endpoint_type)
        return build_control_url(self._base_url, et, rest_api_type, p)

    def build_policy_gen_url(self, request_type: str) -> str:
        return build_policy_gen_url(self._base_url, request_type)

    # -- Header building (shared) --------------------------------------------

    def _build_headers(
        self,
        *,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        feature_overrides: dict[str, Any] | None = None,
        policy_overrides: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        eff_llm_key = _resolve(llm_api_key, self._config.llm_api_key)
        eff_features = _resolve(features, self._config.features)
        eff_policy = _resolve(security_policy, self._config.security_policy)
        eff_config = _resolve(fine_grained_config, self._config.fine_grained_config)
        eff_session = _resolve(session_id, self._session_id)

        features_str = (
            eff_features.dump_for_headers(mode="json_str", overrides=feature_overrides) if eff_features else None
        )
        policy_str = eff_policy.dump_for_headers(mode="json_str", overrides=policy_overrides) if eff_policy else None
        config_str = eff_config.dump_for_headers(mode="json_str", overrides=config_overrides) if eff_config else None

        headers = build_sequrity_headers(
            api_key=self._api_key,
            llm_api_key=eff_llm_key,
            features=features_str,
            policy=policy_str,
            config=config_str,
            session_id=eff_session,
        )
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _track_session(self, response: httpx.Response) -> None:
        new_session = response.headers.get("X-Session-ID")
        if new_session:
            self._session_id = new_session

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
        feature_overrides: dict[str, Any] | None = None,
        policy_overrides: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Async variant of :meth:`ControlSyncTransport.request`."""
        headers = self._build_headers(
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
            feature_overrides=feature_overrides,
            policy_overrides=policy_overrides,
            config_overrides=config_overrides,
            custom_headers=custom_headers,
        )

        try:
            response = await self._http.post(url, json=payload, headers=headers)
        except httpx.ConnectError as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        self._track_session(response)
        return response

    async def stream_request(
        self,
        *,
        url: str,
        payload: dict,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        feature_overrides: dict[str, Any] | None = None,
        policy_overrides: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Open an async streaming POST request.

        Returns the raw ``httpx.Response`` in streaming mode. The caller
        is responsible for closing the response (typically via an
        :class:`AsyncStream` wrapper).

        Raises:
            SequrityAPIError: On HTTP 4xx/5xx responses.
            SequrityConnectionError: On network failures.
        """
        headers = self._build_headers(
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
            feature_overrides=feature_overrides,
            policy_overrides=policy_overrides,
            config_overrides=config_overrides,
            custom_headers=custom_headers,
        )

        request = self._http.build_request("POST", url, json=payload, headers=headers)

        try:
            response = await self._http.send(request, stream=True)
        except httpx.ConnectError as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            await response.aread()  # consume body for error message
            await response.aclose()
            raise SequrityAPIError.from_response(response)

        self._track_session(response)
        return response
