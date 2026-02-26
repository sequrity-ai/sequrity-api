"""Chat completions resource (OpenAI-compatible format)."""

from __future__ import annotations

from typing import Literal, overload

from ..._sentinel import NOT_GIVEN, _NotGiven
from ...types.chat_completion.request import ChatCompletionRequest, Message, ReasoningEffort, ResponseFormat, Tool
from ...types.chat_completion.response import ChatCompletionResponse
from ...types.chat_completion.stream import ChatCompletionChunk
from ...types.enums import LlmServiceProvider, LlmServiceProviderStr, RestApiType
from .._stream import AsyncStream, SyncStream
from .._transport import ControlAsyncTransport, ControlSyncTransport
from ..types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


class ChatResource:
    """OpenAI-compatible chat completions — ``client.control.chat``."""

    def __init__(self, transport: ControlSyncTransport) -> None:
        self._transport = transport

    @overload
    def create(
        self,
        messages: list[Message | dict],
        model: str,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
        tools: list[Tool | dict] | None = None,
        stream: Literal[True],
        seed: int | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        response_format: ResponseFormat | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        custom_headers: dict[str, str] | None = None,
    ) -> SyncStream[ChatCompletionChunk]: ...

    @overload
    def create(
        self,
        messages: list[Message | dict],
        model: str,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
        tools: list[Tool | dict] | None = None,
        stream: Literal[False] | None = None,
        seed: int | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        response_format: ResponseFormat | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        custom_headers: dict[str, str] | None = None,
    ) -> ChatCompletionResponse: ...

    def create(
        self,
        messages: list[Message | dict],
        model: str,
        *,
        # LLM parameters
        temperature: float | None = None,
        top_p: float | None = None,
        tools: list[Tool | dict] | None = None,
        stream: bool | None = None,
        seed: int | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        response_format: ResponseFormat | None = None,
        # Sequrity overrides (NOT_GIVEN -> client defaults)
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        custom_headers: dict[str, str] | None = None,
    ) -> ChatCompletionResponse | SyncStream[ChatCompletionChunk]:
        """Send a chat completion request through Sequrity's secure orchestrator.

        Args:
            messages: List of chat messages in the conversation.
            model: The LLM model identifier (e.g., ``"gpt-4o"``, ``"openai/gpt-5-mini"``).
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            tools: List of tools available to the model.
            stream: Whether to stream the response. When ``True``, returns a
                :class:`SyncStream` of :class:`ChatCompletionChunk` objects.
            seed: Random seed for reproducibility.
            reasoning_effort: Reasoning effort level for supported models.
            response_format: Response format specification.
            provider: LLM service provider override.
            llm_api_key: LLM provider API key override.
            features: Security features override.
            security_policy: Security policy override.
            fine_grained_config: Fine-grained config override.
            endpoint_type: Endpoint type override.
            session_id: Explicit session ID override.

        Returns:
            ``ChatCompletionResponse`` when ``stream`` is ``False``/``None``,
            or ``SyncStream[ChatCompletionChunk]`` when ``stream`` is ``True``.
        """
        payload = ChatCompletionRequest.model_validate(
            {
                "messages": messages,
                "model": model,
                "reasoning_effort": reasoning_effort,
                "response_format": response_format,
                "seed": seed,
                "stream": stream,
                "temperature": temperature,
                "tools": tools,
                "top_p": top_p,
            }
        ).model_dump(exclude_none=True)

        url = self._transport.build_url(
            RestApiType.CHAT_COMPLETIONS,
            provider=provider,
            endpoint_type=endpoint_type,
        )

        if stream:
            response = self._transport.stream_request(
                url=url,
                payload=payload,
                llm_api_key=llm_api_key,
                features=features,
                security_policy=security_policy,
                fine_grained_config=fine_grained_config,
                session_id=session_id,
                custom_headers=custom_headers,
            )
            return SyncStream(response, ChatCompletionChunk, session_id=response.headers.get("X-Session-ID"))

        response = self._transport.request(
            url=url,
            payload=payload,
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
            custom_headers=custom_headers,
        )
        result = ChatCompletionResponse.model_validate(response.json())
        result.session_id = response.headers.get("X-Session-ID")
        return result


class AsyncChatResource:
    """Async variant of :class:`ChatResource`."""

    def __init__(self, transport: ControlAsyncTransport) -> None:
        self._transport = transport

    @overload
    async def create(
        self,
        messages: list[Message | dict],
        model: str,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
        tools: list[Tool | dict] | None = None,
        stream: Literal[True],
        seed: int | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        response_format: ResponseFormat | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> AsyncStream[ChatCompletionChunk]: ...

    @overload
    async def create(
        self,
        messages: list[Message | dict],
        model: str,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
        tools: list[Tool | dict] | None = None,
        stream: Literal[False] | None = None,
        seed: int | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        response_format: ResponseFormat | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> ChatCompletionResponse: ...

    async def create(
        self,
        messages: list[Message | dict],
        model: str,
        *,
        temperature: float | None = None,
        top_p: float | None = None,
        tools: list[Tool | dict] | None = None,
        stream: bool | None = None,
        seed: int | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        response_format: ResponseFormat | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
        custom_headers: dict[str, str] | None = None,
    ) -> ChatCompletionResponse | AsyncStream[ChatCompletionChunk]:
        """Async variant of :meth:`ChatResource.create`."""
        payload = ChatCompletionRequest.model_validate(
            {
                "messages": messages,
                "model": model,
                "reasoning_effort": reasoning_effort,
                "response_format": response_format,
                "seed": seed,
                "stream": stream,
                "temperature": temperature,
                "tools": tools,
                "top_p": top_p,
            }
        ).model_dump(exclude_none=True)

        url = self._transport.build_url(
            RestApiType.CHAT_COMPLETIONS,
            provider=provider,
            endpoint_type=endpoint_type,
        )

        if stream:
            response = await self._transport.stream_request(
                url=url,
                payload=payload,
                llm_api_key=llm_api_key,
                features=features,
                security_policy=security_policy,
                fine_grained_config=fine_grained_config,
                session_id=session_id,
                custom_headers=custom_headers,
            )
            return AsyncStream(response, ChatCompletionChunk, session_id=response.headers.get("X-Session-ID"))

        response = await self._transport.request(
            url=url,
            payload=payload,
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
            custom_headers=custom_headers,
        )
        result = ChatCompletionResponse.model_validate(response.json())
        result.session_id = response.headers.get("X-Session-ID")
        return result
