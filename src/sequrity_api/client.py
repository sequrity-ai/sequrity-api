import os
from typing import Iterable, Literal

import httpx

from .constants import _SEQURITY_BASE_URL
from .types.chat_completion import (
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from .types.chat_completion.request import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)


class SequrityClient:
    def __init__(
        self,
        api_key: str | None = None,
        rest_api_endpoint: str | None = None,
        sequrity_api_key: str | None = None,
    ):
        if sequrity_api_key is None:
            sequrity_api_key = os.getenv("SEQURITY_API_KEY")
        if api_key is None:
            api_key = os.getenv("API_KEY")
        self.sequrity_key = sequrity_api_key
        self.sequrity_url = _SEQURITY_BASE_URL
        self.llm_url = rest_api_endpoint
        self.llm_api_key = api_key

    def create_chat_completion(
        self,
        messages: Iterable[ChatCompletionMessageParam],
        model: str,
        headers: dict | None = None,
        session_id: str | None = None,
        frequency_penalty: float | None = None,
        function_call: str | dict | None = None,
        functions: Iterable[dict] | None = None,
        logit_bias: dict[str, int] | None = None,
        logprobs: bool | None = None,
        max_completion_tokens: int | None = None,
        max_tokens: int | None = None,
        modalities: list[Literal["text", "audio"]] | None = None,
        parallel_tool_calls: bool | None = None,
        presence_penalty: float | None = None,
        reasoning_effort: Literal["minimal", "low", "medium", "high"] | None = None,
        seed: int | None = None,
        stop: str | list[str] | None = None,
        store: bool | None = None,
        stream: bool | None = None,
        temperature: float | None = None,
        tools: list[ChatCompletionToolParam] | None = None,
        top_logprobs: int | None = None,
        top_p: float | None = None,
        verbosity: Literal["low", "medium", "high"] | None = None,
        timeout: int = 300,
    ) -> ChatCompletionResponse:
        request = ChatCompletionRequest(
            messages=messages,
            model=model,
            frequency_penalty=frequency_penalty,
            function_call=function_call,
            functions=functions,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_completion_tokens=max_completion_tokens,
            max_tokens=max_tokens,
            modalities=modalities,
            parallel_tool_calls=parallel_tool_calls,
            presence_penalty=presence_penalty,
            reasoning_effort=reasoning_effort,
            seed=seed,
            stop=stop,
            store=store,
            stream=stream,
            temperature=temperature,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            verbosity=verbosity,
        )

        """
        x_model_name: str = Header(None),
        x_api_key: str = Header(None),
        x_rest_api_endpoint: str = Header(None),
        x_sequrity_api_key: str = Header(None),
        x_session_id: str = Header(None),
        """
        if headers is None:
            headers = {}
        if self.sequrity_key is None and "X-Sequrity-Api-Key" not in headers:
            raise ValueError(
                "Sequrity API key is required. Please set in in the header using 'X-Sequrity-Api-Key'."
            )
        if self.llm_api_key is None and "Authorization" not in headers:
            raise ValueError(
                "API key of LLM service provider is required. Please set it in the header using 'Authorization'."
            )
        if self.llm_url is None and "X-Rest-Api-Endpoint" not in headers:
            raise ValueError(
                "Rest API endpoint of LLM service provider is required. Please set it in the header using 'X-Rest-Api-Endpoint'."
            )

        if self.sequrity_key is not None and "X-Sequrity-Api-Key" not in headers:
            headers["X-Sequrity-Api-Key"] = self.sequrity_key
        if self.llm_api_key is not None and "X-Api-Key" not in headers:
            headers["X-Api-Key"] = self.llm_api_key
        if self.llm_url is not None and "X-Rest-Api-Endpoint" not in headers:
            headers["X-Rest-Api-Endpoint"] = self.llm_url
        if "X-Model-Name" not in headers:
            headers["X-Model-Name"] = model
        if session_id is not None and "X-Session-Id" not in headers:
            headers["X-Session-Id"] = session_id

        headers["Content-Type"] = "application/json"
        payload = request.model_dump(mode="json", exclude_none=True)
        response = httpx.post(
            f"{self.sequrity_url}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        # get session id from response headers
        session_id = response.headers["X-Session-Id"]
        response_data = response.json()
        response_data["session_id"] = session_id
        so_response = ChatCompletionResponse.model_validate(response_data)
        return so_response
