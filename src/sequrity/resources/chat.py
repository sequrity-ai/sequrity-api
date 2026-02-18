"""Chat completions resource (OpenAI-compatible format)."""

from __future__ import annotations

from .._sentinel import NOT_GIVEN, _NotGiven
from .._transport import AsyncTransport, SyncTransport
from ..types.chat_completion.request import ChatCompletionRequest, Message, ReasoningEffort, ResponseFormat, Tool
from ..types.chat_completion.response import ChatCompletionResponse
from ..types.enums import RestApiType
from ..types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


class ChatResource:
    """OpenAI-compatible chat completions — ``client.chat``."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

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
        # Sequrity overrides (NOT_GIVEN → client defaults)
        provider: str | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> ChatCompletionResponse:
        """Send a chat completion request through Sequrity's secure orchestrator.

        Args:
            messages: List of chat messages in the conversation.
            model: The LLM model identifier (e.g., ``"gpt-4o"``, ``"openai/gpt-5-mini"``).
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            tools: List of tools available to the model.
            stream: Whether to stream the response.
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
            Parsed ``ChatCompletionResponse`` with ``session_id`` populated.
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
            RestApiType.CHAT_COMPLETIONS, provider=provider, endpoint_type=endpoint_type,
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

        result = ChatCompletionResponse.model_validate(response.json())
        result.session_id = response.headers.get("X-Session-ID")
        return result


class AsyncChatResource:
    """Async variant of :class:`ChatResource`."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

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
        provider: str | None | _NotGiven = NOT_GIVEN,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
        features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
        security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
        fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
        endpoint_type: str | _NotGiven = NOT_GIVEN,
        session_id: str | None | _NotGiven = NOT_GIVEN,
    ) -> ChatCompletionResponse:
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
            RestApiType.CHAT_COMPLETIONS, provider=provider, endpoint_type=endpoint_type,
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

        result = ChatCompletionResponse.model_validate(response.json())
        result.session_id = response.headers.get("X-Session-ID")
        return result
