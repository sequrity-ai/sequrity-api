from typing import Literal
from urllib.parse import urljoin

import httpx

from ..constants import CONTROL_API_PATHS
from ..service_provider import LlmServiceProviderEnum
from ..types.chat_completion.request import ChatCompletionRequest, Message, ReasoningEffort, ResponseFormat, Tool
from ..types.chat_completion.response import ChatCompletionResponse
from ..types.control.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


def create_chat_completion(
    client: httpx.Client,
    base_url: str,
    api_key: str,
    messages: list[Message] | list[dict],
    model: str,
    llm_api_key: str | None,
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
    # Construct the URL based on service provider
    if service_provider == "default":
        path = CONTROL_API_PATHS["chat_completions"]["default"]
    else:
        path = CONTROL_API_PATHS["chat_completions"]["with_service_provider"].format(service_provider=service_provider)
    url = urljoin(base_url, path)

    # Prepare the request payload
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

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if llm_api_key:
        headers["X-Api-Key"] = llm_api_key
    if features:
        headers["X-Security-Features"] = features.dump_for_headers(mode="json_str")
    if security_policy:
        headers["X-Security-Policy"] = security_policy.dump_for_headers(mode="json_str")
    if fine_grained_config:
        headers["X-Security-Config"] = fine_grained_config.dump_for_headers(mode="json_str")
    if session_id:
        headers["X-Session-Id"] = session_id

    # Make the HTTP request
    response = client.post(url, json=payload, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    session_id = response.headers.get("X-Session-Id")

    # Parse and return the response
    response = ChatCompletionResponse.model_validate(response_data)
    response.session_id = session_id
    if return_type == "json":
        return response.model_dump(mode="json")
    elif return_type == "python":
        return response
    else:
        raise ValueError(f"Invalid return_type: {return_type}")
