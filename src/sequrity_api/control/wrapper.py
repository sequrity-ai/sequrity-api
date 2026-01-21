from typing import Literal

import httpx

from ..service_provider import LlmServiceProviderEnum
from ..types.chat_completion.request import Message, ReasoningEffort, ResponseFormat, Tool
from ..types.chat_completion.response import ChatCompletionResponse
from ..types.control.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader
from .sync import create_chat_completion as create_chat_completion_sync


class ControlAPIWrapper:
    def __init__(self, client: httpx.Client, base_url: str, api_key: str):
        self.client = client
        self.base_url = base_url
        self.sqrt_api_key = api_key

    def create_chat_completion(
        self,
        messages: list[Message],
        model: str,
        llm_api_key: str | None = None,
        features: FeaturesHeader | None = None,
        security_policy: SecurityPolicyHeader | None = None,
        fine_grained_config: FineGrainedConfigHeader | None = None,
        service_provider: LlmServiceProviderEnum | Literal["default"] = "default",
        session_id: str | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        response_format: ResponseFormat | None = None,
        seed: int | None = None,
        stream: bool | None = None,
        temperature: float | None = None,
        tools: list[Tool] | None = None,
        top_p: float | None = None,
        return_type: Literal["python", "json"] = "python",
    ) -> ChatCompletionResponse | dict:
        """Send a chat completion request. See :func:`.sync.create_chat_completion` for details."""
        return create_chat_completion_sync(
            client=self.client,
            base_url=self.base_url,
            api_key=self.sqrt_api_key,
            messages=messages,
            model=model,
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            service_provider=service_provider,
            session_id=session_id,
            reasoning_effort=reasoning_effort,
            response_format=response_format,
            seed=seed,
            stream=stream,
            temperature=temperature,
            tools=tools,
            top_p=top_p,
            return_type=return_type,
        )
