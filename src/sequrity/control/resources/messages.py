"""Anthropic Messages resource."""

from __future__ import annotations

from typing import Literal

from ..._sentinel import NOT_GIVEN, _NotGiven
from ...types.enums import RestApiType
from ...types.messages.request import (
    AnthropicMessageRequest,
    MessageParam,
    MetadataParam,
    OutputConfigParam,
    TextBlockParam,
    ThinkingConfigParam,
    ToolChoiceParam,
    ToolParam,
)
from ...types.messages.response import AnthropicMessageResponse
from .._transport import ControlAsyncTransport, ControlSyncTransport
from ..types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


class MessagesResource:
    """Anthropic Messages API — ``client.control.messages``."""

    def __init__(self, transport: ControlSyncTransport) -> None:
        self._transport = transport

    def create(
        self,
        messages: list[MessageParam | dict],
        model: str,
        max_tokens: int,
        *,
        # Anthropic parameters
        system: str | list[TextBlockParam] | list[dict] | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        tools: list[ToolParam | dict] | None = None,
        tool_choice: ToolChoiceParam | dict | None = None,
        thinking: ThinkingConfigParam | dict | None = None,
        stop_sequences: list[str] | None = None,
        stream: bool | None = None,
        output_config: OutputConfigParam | dict | None = None,
        metadata: MetadataParam | dict | None = None,
        service_tier: Literal["auto", "standard_only"] | None = None,
        timeout: float | None = None,
        # Sequrity overrides (NOT_GIVEN -> client defaults)
        provider: str | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> AnthropicMessageResponse:
        """Send an Anthropic Messages API request through Sequrity.

        Args:
            messages: List of messages with alternating user and assistant turns.
            model: The model identifier (e.g., ``"claude-4-sonnet"``).
            max_tokens: Maximum number of tokens to generate before stopping.
            system: System prompt as a string or list of text blocks.
            temperature: Sampling temperature (0.0 to 1.0).
            top_p: Nucleus sampling probability threshold.
            top_k: Only sample from the top K options for each token.
            tools: List of tool definitions available to the model.
            tool_choice: How the model should use the provided tools.
            thinking: Configuration for extended thinking.
            stop_sequences: Custom text sequences that cause the model to stop.
            stream: Whether to stream the response.
            output_config: Output format configuration.
            metadata: Request metadata.
            service_tier: Priority or standard capacity selection.
            timeout: Maximum request duration in seconds.
            provider: LLM service provider override.
            llm_api_key: LLM provider API key override.
            features: Security features override.
            security_policy: Security policy override.
            fine_grained_config: Fine-grained config override.
            endpoint_type: Endpoint type override.
            session_id: Explicit session ID override.

        Returns:
            Parsed ``AnthropicMessageResponse`` with ``session_id`` populated.
        """
        payload = AnthropicMessageRequest.model_validate(
            {
                "messages": messages,
                "model": model,
                "max_tokens": max_tokens,
                "system": system,
                "stop_sequences": stop_sequences,
                "stream": stream,
                "temperature": temperature,
                "tools": tools,
                "tool_choice": tool_choice,
                "thinking": thinking,
                "top_k": top_k,
                "top_p": top_p,
                "output_config": output_config,
                "metadata": metadata,
                "service_tier": service_tier,
                "timeout": timeout,
            }
        ).model_dump(exclude_none=True)

        url = self._transport.build_url(
            RestApiType.MESSAGES,
            provider=provider,
            endpoint_type=endpoint_type,
        )

        response = self._transport.request(
            url=url,
            payload=payload,
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
        )

        result = AnthropicMessageResponse.model_validate(response.json())
        result.session_id = response.headers.get("X-Session-ID")
        return result


class AsyncMessagesResource:
    """Async variant of :class:`MessagesResource`."""

    def __init__(self, transport: ControlAsyncTransport) -> None:
        self._transport = transport

    async def create(
        self,
        messages: list[MessageParam | dict],
        model: str,
        max_tokens: int,
        *,
        system: str | list[TextBlockParam] | list[dict] | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        tools: list[ToolParam | dict] | None = None,
        tool_choice: ToolChoiceParam | dict | None = None,
        thinking: ThinkingConfigParam | dict | None = None,
        stop_sequences: list[str] | None = None,
        stream: bool | None = None,
        output_config: OutputConfigParam | dict | None = None,
        metadata: MetadataParam | dict | None = None,
        service_tier: Literal["auto", "standard_only"] | None = None,
        timeout: float | None = None,
        provider: str | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = None,
    ) -> AnthropicMessageResponse:
        """Async variant of :meth:`MessagesResource.create`."""
        payload = AnthropicMessageRequest.model_validate(
            {
                "messages": messages,
                "model": model,
                "max_tokens": max_tokens,
                "system": system,
                "stop_sequences": stop_sequences,
                "stream": stream,
                "temperature": temperature,
                "tools": tools,
                "tool_choice": tool_choice,
                "thinking": thinking,
                "top_k": top_k,
                "top_p": top_p,
                "output_config": output_config,
                "metadata": metadata,
                "service_tier": service_tier,
                "timeout": timeout,
            }
        ).model_dump(exclude_none=True)

        url = self._transport.build_url(
            RestApiType.MESSAGES,
            provider=provider,
            endpoint_type=endpoint_type,
        )

        response = await self._transport.request(
            url=url,
            payload=payload,
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            session_id=session_id,
        )

        result = AnthropicMessageResponse.model_validate(response.json())
        result.session_id = response.headers.get("X-Session-ID")
        return result
