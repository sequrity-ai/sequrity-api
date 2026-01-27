import json
from typing import Callable, Literal
from urllib.parse import urljoin

import httpx

from ...constants import CONTROL_API_PATHS
from ...service_provider import LlmServiceProviderEnum
from ..types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader
from ..types.langgraph import LangGraphChatCompletionRequest, LangGraphChatCompletionResponse
from ..types.results import ResponseContentJsonSchema
from ..types.value_with_meta import MetaData, ValueWithMeta

try:
    from langgraph.graph import StateGraph

    from .graph_executor import LangGraphExecutor

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


def create_langgraph_chat_completion_sync(
    client: httpx.Client,
    url: str,
    api_key: str,
    llm_api_key: str | None,
    request: LangGraphChatCompletionRequest,
    features: FeaturesHeader | None = None,
    security_policy: SecurityPolicyHeader | None = None,
    fine_grained_config: FineGrainedConfigHeader | None = None,
    session_id: str | None = None,
    timeout: float = 300.0,
    return_type: Literal["python", "json"] = "python",
) -> LangGraphChatCompletionResponse | dict:
    # Prepare the request payload
    payload = request.model_dump(mode="json", exclude_none=True, exclude={"response_format", "top_p"})
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
    response = client.post(url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    response_data = response.json()
    session_id = response.headers.get("X-Session-Id")

    # Parse and return the response
    response = LangGraphChatCompletionResponse.model_validate(response_data)
    response.session_id = session_id
    if return_type == "json":
        return response.model_dump(mode="json", exclude_none=True, exclude={"response_format", "top_p"})
    elif return_type == "python":
        return response
    else:
        raise ValueError(f"Invalid return_type: {return_type}")


def run_graph_sync(
    client: httpx.Client,
    base_url: str,
    api_key: str,
    model: str,
    llm_api_key: str | None,
    graph: "StateGraph",
    initial_state: dict,
    features: FeaturesHeader,
    initial_state_meta: MetaData | None = None,
    max_exec_steps: int = 20,
    security_policy: SecurityPolicyHeader | None = None,
    fine_grained_config: FineGrainedConfigHeader | None = None,
    service_provider: LlmServiceProviderEnum = LlmServiceProviderEnum.OPENROUTER,
    node_functions: dict[str, Callable] | None = None,
    internal_node_mapping: dict[str, str] | None = None,
    timeout: float = 300.0,
) -> dict:
    if features.llm.feature_name != "Dual LLM":
        raise ValueError("LangGraph execution requires 'Dual LLM' feature to be enabled.")
    if fine_grained_config.response_format.strip_response_content:
        raise ValueError("LangGraph execution requires 'strip_response_content' to be False.")
    if fine_grained_config.disable_rllm is not True:
        fine_grained_config.disable_rllm = True

    executor = LangGraphExecutor(
        graph=graph,
        node_functions=node_functions,
        internal_node_mapping=internal_node_mapping,
    )
    tools = executor.build_tool_definitions()

    if initial_state_meta is None:
        initial_state_meta = MetaData(producers=set(), consumers={"*"}, tags=set())

    predefined_vars_with_meta = {"initial_state": ValueWithMeta(value=initial_state, meta=initial_state_meta)}

    messages = [
        {
            "role": "user",
            "content": f"Execute the LangGraph StateGraph with initial_state: {json.dumps(initial_state, default=str)}.",
        }
    ]

    current_state = initial_state.copy()
    final_state = None
    url_path = CONTROL_API_PATHS["langgraph_chat_completions"]["default"].format(service_provider=service_provider)
    url = urljoin(base_url, url_path)
    session_id = None

    for step in range(max_exec_steps):
        request = LangGraphChatCompletionRequest.model_validate(
            {
                "messages": messages,
                "model": model,
                "tools": tools if tools else None,
                "user_provided_program": executor.generated_code,
                "predefined_vars_with_meta": predefined_vars_with_meta,
            }
        )
        response = create_langgraph_chat_completion_sync(
            client=client,
            url=url,
            api_key=api_key,
            llm_api_key=llm_api_key,
            request=request,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            timeout=timeout,
            session_id=session_id,
        )
        session_id = response.session_id
        tool_calls = response.choices[0].message.tool_calls
        content = ResponseContentJsonSchema.parse_raw(response.choices[0].message.content)

        if response.choices[0].finish_reason != "tool_calls":
            final_state = current_state
            break

        if tool_calls is None and content.status != "success":
            raise RuntimeError(f"Graph execution failed at step {step}: {content.error}")

        # append tool call message
        messages.append(response.choices[0].message.model_dump(mode="json"))

        if not tool_calls:
            raise RuntimeError(f"No tool calls found in response at step {step} but finish_reason was 'tool_calls'.")

        for tool_call in tool_calls:
            tool_result = executor.execute_tool_call(tool_call.model_dump(mode="json"))

            # Update current state with result
            # Nodes return dicts that should be merged into state
            if isinstance(tool_result, dict):
                for key, value in tool_result.items():
                    if key in current_state and isinstance(value, list) and isinstance(current_state[key], list):
                        # Extend lists
                        current_state[key].extend(value)
                    else:
                        # Overwrite or add new keys
                        current_state[key] = value

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, default=str),
                }
            )

    if final_state is None:
        raise RuntimeError(f"Graph did not complete within {max_exec_steps} steps.")
    return final_state
