"""OpenAI Responses API resource."""

from __future__ import annotations

from typing import Literal, overload

from ..._sentinel import NOT_GIVEN, _NotGiven
from ...types.enums import LlmServiceProvider, LlmServiceProviderStr, RestApiType
from ...types.responses.request import (
    ConversationParam,
    ReasoningParam,
    ResponsePromptParam,
    ResponsesRequest,
    ResponseTextConfigParam,
    StreamOptionsParam,
    ToolChoiceFunctionParam,
    ToolParam,
)
from ...types.responses.response import ResponsesResponse
from ...types.responses.stream import OpenAiResponseStreamEvent
from .._stream import AsyncStream, SyncStream
from .._transport import ControlAsyncTransport, ControlSyncTransport
from ..types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


class ResponsesResource:
    """OpenAI Responses API — ``client.control.responses``."""

    def __init__(self, transport: ControlSyncTransport) -> None:
        self._transport = transport

    @overload
    def create(
        self,
        model: str,
        *,
        input: str | list | None = None,
        instructions: str | None = None,
        tools: list[ToolParam | dict] | None = None,
        tool_choice: Literal["none", "auto", "required"] | ToolChoiceFunctionParam | dict | None = None,
        stream: Literal[True],
        temperature: float | None = None,
        top_p: float | None = None,
        max_output_tokens: int | None = None,
        reasoning: ReasoningParam | dict | None = None,
        text: ResponseTextConfigParam | dict | None = None,
        metadata: dict[str, str] | None = None,
        previous_response_id: str | None = None,
        include: list[str] | None = None,
        store: bool | None = None,
        truncation: Literal["auto", "disabled"] | None = None,
        parallel_tool_calls: bool | None = None,
        max_tool_calls: int | None = None,
        background: bool | None = None,
        conversation: str | ConversationParam | dict | None = None,
        prompt: ResponsePromptParam | dict | None = None,
        service_tier: Literal["auto", "default", "flex", "scale", "priority"] | None = None,
        stream_options: StreamOptionsParam | dict | None = None,
        top_logprobs: int | None = None,
        timeout: float | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> SyncStream[OpenAiResponseStreamEvent]: ...

    @overload
    def create(
        self,
        model: str,
        *,
        input: str | list | None = None,
        instructions: str | None = None,
        tools: list[ToolParam | dict] | None = None,
        tool_choice: Literal["none", "auto", "required"] | ToolChoiceFunctionParam | dict | None = None,
        stream: Literal[False] | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_output_tokens: int | None = None,
        reasoning: ReasoningParam | dict | None = None,
        text: ResponseTextConfigParam | dict | None = None,
        metadata: dict[str, str] | None = None,
        previous_response_id: str | None = None,
        include: list[str] | None = None,
        store: bool | None = None,
        truncation: Literal["auto", "disabled"] | None = None,
        parallel_tool_calls: bool | None = None,
        max_tool_calls: int | None = None,
        background: bool | None = None,
        conversation: str | ConversationParam | dict | None = None,
        prompt: ResponsePromptParam | dict | None = None,
        service_tier: Literal["auto", "default", "flex", "scale", "priority"] | None = None,
        stream_options: StreamOptionsParam | dict | None = None,
        top_logprobs: int | None = None,
        timeout: float | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> ResponsesResponse: ...

    def create(
        self,
        model: str,
        *,
        # Responses API parameters
        input: str | list | None = None,
        instructions: str | None = None,
        tools: list[ToolParam | dict] | None = None,
        tool_choice: Literal["none", "auto", "required"] | ToolChoiceFunctionParam | dict | None = None,
        stream: bool | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_output_tokens: int | None = None,
        reasoning: ReasoningParam | dict | None = None,
        text: ResponseTextConfigParam | dict | None = None,
        metadata: dict[str, str] | None = None,
        previous_response_id: str | None = None,
        include: list[str] | None = None,
        store: bool | None = None,
        truncation: Literal["auto", "disabled"] | None = None,
        parallel_tool_calls: bool | None = None,
        max_tool_calls: int | None = None,
        background: bool | None = None,
        conversation: str | ConversationParam | dict | None = None,
        prompt: ResponsePromptParam | dict | None = None,
        service_tier: Literal["auto", "default", "flex", "scale", "priority"] | None = None,
        stream_options: StreamOptionsParam | dict | None = None,
        top_logprobs: int | None = None,
        timeout: float | None = None,
        # Sequrity overrides (NOT_GIVEN -> client defaults)
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> ResponsesResponse | SyncStream[OpenAiResponseStreamEvent]:
        """Send a Responses API request through Sequrity's secure orchestrator.

        Args:
            model: The LLM model identifier (e.g., ``"gpt-4o"``, ``"o3"``).
            input: Text, image, or file inputs to the model.
            instructions: A system (or developer) message.
            tools: List of tools available to the model.
            tool_choice: How the model should select which tool to use.
            stream: Whether to stream the response. When ``True``, returns a
                :class:`SyncStream` of :class:`OpenAiResponseStreamEvent` objects.
            temperature: Sampling temperature (0-2).
            top_p: Nucleus sampling parameter.
            max_output_tokens: Upper bound for generated tokens.
            reasoning: Configuration for reasoning models.
            text: Text response format configuration.
            metadata: Key-value pairs attached to the response.
            previous_response_id: ID of the previous response for multi-turn.
            include: Additional output data to include.
            store: Whether to store the response for later retrieval.
            truncation: Truncation strategy for the response.
            parallel_tool_calls: Whether to allow parallel tool execution.
            max_tool_calls: Maximum number of calls to built-in tools.
            background: Whether to run the response in the background.
            conversation: Conversation context.
            prompt: Prompt template reference.
            service_tier: Processing tier for serving the request.
            stream_options: Options for streaming responses.
            top_logprobs: Number of most likely tokens to return (0-20).
            timeout: Client-side timeout in seconds.
            provider: LLM service provider override.
            llm_api_key: LLM provider API key override.
            features: Security features override.
            security_policy: Security policy override.
            fine_grained_config: Fine-grained config override.
            endpoint_type: Endpoint type override.
            session_id: Explicit session ID override.

        Returns:
            ``ResponsesResponse`` when ``stream`` is ``False``/``None``,
            or ``SyncStream[OpenAiResponseStreamEvent]`` when ``stream`` is ``True``.
        """
        payload = ResponsesRequest.model_validate(
            {
                "model": model,
                "input": input,
                "instructions": instructions,
                "tools": tools,
                "tool_choice": tool_choice,
                "stream": stream,
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_output_tokens,
                "reasoning": reasoning,
                "text": text,
                "metadata": metadata,
                "previous_response_id": previous_response_id,
                "include": include,
                "store": store,
                "truncation": truncation,
                "parallel_tool_calls": parallel_tool_calls,
                "max_tool_calls": max_tool_calls,
                "background": background,
                "conversation": conversation,
                "prompt": prompt,
                "service_tier": service_tier,
                "stream_options": stream_options,
                "top_logprobs": top_logprobs,
                "timeout": timeout,
            }
        ).model_dump(exclude_none=True)

        url = self._transport.build_url(
            RestApiType.RESPONSES,
            provider=provider,
            endpoint_type=endpoint_type,
        )

        sequrity_kwargs = dict(
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
        )

        if stream:
            response = self._transport.stream_request(url=url, payload=payload, **sequrity_kwargs)
            return SyncStream(response, OpenAiResponseStreamEvent, session_id=response.headers.get("X-Session-ID"))

        response = self._transport.request(url=url, payload=payload, **sequrity_kwargs)
        result = ResponsesResponse.model_validate(response.json())
        result.session_id = response.headers.get("X-Session-ID")
        return result


class AsyncResponsesResource:
    """Async variant of :class:`ResponsesResource`."""

    def __init__(self, transport: ControlAsyncTransport) -> None:
        self._transport = transport

    @overload
    async def create(
        self,
        model: str,
        *,
        input: str | list | None = None,
        instructions: str | None = None,
        tools: list[ToolParam | dict] | None = None,
        tool_choice: Literal["none", "auto", "required"] | ToolChoiceFunctionParam | dict | None = None,
        stream: Literal[True],
        temperature: float | None = None,
        top_p: float | None = None,
        max_output_tokens: int | None = None,
        reasoning: ReasoningParam | dict | None = None,
        text: ResponseTextConfigParam | dict | None = None,
        metadata: dict[str, str] | None = None,
        previous_response_id: str | None = None,
        include: list[str] | None = None,
        store: bool | None = None,
        truncation: Literal["auto", "disabled"] | None = None,
        parallel_tool_calls: bool | None = None,
        max_tool_calls: int | None = None,
        background: bool | None = None,
        conversation: str | ConversationParam | dict | None = None,
        prompt: ResponsePromptParam | dict | None = None,
        service_tier: Literal["auto", "default", "flex", "scale", "priority"] | None = None,
        stream_options: StreamOptionsParam | dict | None = None,
        top_logprobs: int | None = None,
        timeout: float | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> AsyncStream[OpenAiResponseStreamEvent]: ...

    @overload
    async def create(
        self,
        model: str,
        *,
        input: str | list | None = None,
        instructions: str | None = None,
        tools: list[ToolParam | dict] | None = None,
        tool_choice: Literal["none", "auto", "required"] | ToolChoiceFunctionParam | dict | None = None,
        stream: Literal[False] | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_output_tokens: int | None = None,
        reasoning: ReasoningParam | dict | None = None,
        text: ResponseTextConfigParam | dict | None = None,
        metadata: dict[str, str] | None = None,
        previous_response_id: str | None = None,
        include: list[str] | None = None,
        store: bool | None = None,
        truncation: Literal["auto", "disabled"] | None = None,
        parallel_tool_calls: bool | None = None,
        max_tool_calls: int | None = None,
        background: bool | None = None,
        conversation: str | ConversationParam | dict | None = None,
        prompt: ResponsePromptParam | dict | None = None,
        service_tier: Literal["auto", "default", "flex", "scale", "priority"] | None = None,
        stream_options: StreamOptionsParam | dict | None = None,
        top_logprobs: int | None = None,
        timeout: float | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> ResponsesResponse: ...

    async def create(
        self,
        model: str,
        *,
        input: str | list | None = None,
        instructions: str | None = None,
        tools: list[ToolParam | dict] | None = None,
        tool_choice: Literal["none", "auto", "required"] | ToolChoiceFunctionParam | dict | None = None,
        stream: bool | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_output_tokens: int | None = None,
        reasoning: ReasoningParam | dict | None = None,
        text: ResponseTextConfigParam | dict | None = None,
        metadata: dict[str, str] | None = None,
        previous_response_id: str | None = None,
        include: list[str] | None = None,
        store: bool | None = None,
        truncation: Literal["auto", "disabled"] | None = None,
        parallel_tool_calls: bool | None = None,
        max_tool_calls: int | None = None,
        background: bool | None = None,
        conversation: str | ConversationParam | dict | None = None,
        prompt: ResponsePromptParam | dict | None = None,
        service_tier: Literal["auto", "default", "flex", "scale", "priority"] | None = None,
        stream_options: StreamOptionsParam | dict | None = None,
        top_logprobs: int | None = None,
        timeout: float | None = None,
        provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> ResponsesResponse | AsyncStream[OpenAiResponseStreamEvent]:
        """Async variant of :meth:`ResponsesResource.create`."""
        payload = ResponsesRequest.model_validate(
            {
                "model": model,
                "input": input,
                "instructions": instructions,
                "tools": tools,
                "tool_choice": tool_choice,
                "stream": stream,
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_output_tokens,
                "reasoning": reasoning,
                "text": text,
                "metadata": metadata,
                "previous_response_id": previous_response_id,
                "include": include,
                "store": store,
                "truncation": truncation,
                "parallel_tool_calls": parallel_tool_calls,
                "max_tool_calls": max_tool_calls,
                "background": background,
                "conversation": conversation,
                "prompt": prompt,
                "service_tier": service_tier,
                "stream_options": stream_options,
                "top_logprobs": top_logprobs,
                "timeout": timeout,
            }
        ).model_dump(exclude_none=True)

        url = self._transport.build_url(
            RestApiType.RESPONSES,
            provider=provider,
            endpoint_type=endpoint_type,
        )

        sequrity_kwargs = dict(
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
        )

        if stream:
            response = await self._transport.stream_request(url=url, payload=payload, **sequrity_kwargs)
            return AsyncStream(response, OpenAiResponseStreamEvent, session_id=response.headers.get("X-Session-ID"))

        response = await self._transport.request(url=url, payload=payload, **sequrity_kwargs)
        result = ResponsesResponse.model_validate(response.json())
        result.session_id = response.headers.get("X-Session-ID")
        return result
