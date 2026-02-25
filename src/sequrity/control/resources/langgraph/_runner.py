"""LangGraph execution loop using the Sequrity Control transport layer."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Callable

from ..._constants import build_sequrity_headers
from ...._exceptions import SequrityAPIError, SequrityConnectionError
from ...._sentinel import NOT_GIVEN, _NotGiven
from ..._transport import ControlSyncTransport, _resolve
from ...types.dual_llm_response import MetaData, ResponseContentJsonSchema, ValueWithMeta
from ...types.enums import EndpointType
from ....types.enums import LlmServiceProvider, LlmServiceProviderStr, RestApiType
from ...types.headers import FeaturesHeader, FineGrainedConfigHeader, FsmOverrides, SecurityPolicyHeader
from ....types.messages.response import AnthropicMessageResponse, ToolUseBlock
from ._types import (
    LangGraphChatCompletionRequest,
    LangGraphChatCompletionResponse,
    LangGraphMessagesRequest,
)

if TYPE_CHECKING:
    from langgraph.graph import StateGraph

try:
    from ._executor import LangGraphExecutor

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


def _update_state(current_state: dict, tool_result: dict) -> None:
    """Merge tool result into current state in-place."""
    for key, value in tool_result.items():
        if key in current_state and isinstance(value, list) and isinstance(current_state[key], list):
            current_state[key].extend(value)
        else:
            current_state[key] = value


def _post_request(
    transport: ControlSyncTransport,
    url: str,
    payload: dict,
    headers: dict[str, str],
    timeout: float,
) -> tuple[dict, str | None]:
    """POST payload and return (response_data, new_session_id)."""
    try:
        http_response = transport._http.post(url, json=payload, headers=headers, timeout=timeout)
    except Exception as exc:
        raise SequrityConnectionError(str(exc)) from exc

    if http_response.status_code >= 400:
        raise SequrityAPIError.from_response(http_response)

    return http_response.json(), http_response.headers.get("X-Session-ID")


def _run_chat_completions_loop(
    transport: ControlSyncTransport,
    executor: LangGraphExecutor,
    *,
    url: str,
    model: str,
    tools: list[dict],
    messages: list[dict],
    current_state: dict,
    context_vars: dict[str, ValueWithMeta],
    max_exec_steps: int,
    timeout: float,
    build_headers: Callable[..., dict[str, str]],
    session_id: str | None,
) -> dict:
    """Execution loop for OpenAI-compatible providers (chat/completions)."""
    for step in range(max_exec_steps):
        request = LangGraphChatCompletionRequest.model_validate(
            {
                "messages": messages,
                "model": model,
                "tools": tools if tools else None,
                "user_provided_program": executor.generated_code,
                "context_vars": context_vars,
            }
        )
        payload = request.model_dump(mode="json", exclude_none=True, exclude={"response_format", "top_p"})
        headers = build_headers(session_id=session_id)

        response_data, new_session = _post_request(transport, url, payload, headers, timeout)
        if new_session:
            session_id = new_session
            transport._session_id = new_session

        response = LangGraphChatCompletionResponse.model_validate(response_data)
        response.session_id = session_id

        tool_calls = response.choices[0].message.tool_calls
        message_content = response.choices[0].message.content
        if message_content is not None:
            content = ResponseContentJsonSchema.parse_json_safe(message_content)
        else:
            content = None

        if response.choices[0].finish_reason != "tool_calls":
            return current_state

        if tool_calls is None and (content is None or content.status != "success"):
            raise RuntimeError(
                f"Graph execution failed at step {step}: {content.error if content else 'No content returned.'}"
            )

        messages.append(response.choices[0].message.model_dump(mode="json"))

        if not tool_calls:
            raise RuntimeError(f"No tool calls found in response at step {step} but finish_reason was 'tool_calls'.")

        for tool_call in tool_calls:
            tool_result = executor.execute_tool_call(
                tool_call.model_dump(mode="json"),
                RestApiType.CHAT_COMPLETIONS,
            )
            if isinstance(tool_result, dict):
                _update_state(current_state, tool_result)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, default=str),
                }
            )

    raise RuntimeError(f"Graph did not complete within {max_exec_steps} steps.")


def _run_messages_loop(
    transport: ControlSyncTransport,
    executor: LangGraphExecutor,
    *,
    url: str,
    model: str,
    tools: list[dict],
    messages: list[dict],
    current_state: dict,
    context_vars: dict[str, ValueWithMeta],
    max_exec_steps: int,
    timeout: float,
    build_headers: Callable[..., dict[str, str]],
    session_id: str | None,
) -> dict:
    """Execution loop for the Anthropic Messages provider."""
    for step in range(max_exec_steps):
        request = LangGraphMessagesRequest.model_validate(
            {
                "messages": messages,
                "model": model,
                "max_tokens": 16384,
                "tools": tools if tools else None,
                "user_provided_program": executor.generated_code,
                "context_vars": context_vars,
            }
        )
        payload = request.model_dump(mode="json", exclude_none=True)
        headers = build_headers(session_id=session_id)

        response_data, new_session = _post_request(transport, url, payload, headers, timeout)
        if new_session:
            session_id = new_session
            transport._session_id = new_session

        response = AnthropicMessageResponse.model_validate(response_data)
        response.session_id = session_id

        tool_use_blocks = [b for b in response.content if isinstance(b, ToolUseBlock)]

        if response.stop_reason != "tool_use":
            return current_state

        if not tool_use_blocks:
            raise RuntimeError(f"No tool_use blocks in response at step {step} but stop_reason was 'tool_use'.")

        # Append assistant turn with full content blocks
        messages.append(
            {
                "role": "assistant",
                "content": [b.model_dump(mode="json") for b in response.content],
            }
        )

        # Execute each tool and build tool_result blocks
        tool_result_blocks = []
        for block in tool_use_blocks:
            tool_result = executor.execute_tool_call(
                block.model_dump(mode="json"),
                RestApiType.MESSAGES,
            )
            if isinstance(tool_result, dict):
                _update_state(current_state, tool_result)

            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(tool_result, default=str),
                }
            )

        messages.append(
            {
                "role": "user",
                "content": tool_result_blocks,
            }
        )

    raise RuntimeError(f"Graph did not complete within {max_exec_steps} steps.")


def run_graph_sync(
    transport: ControlSyncTransport,
    model: str,
    graph: StateGraph,
    initial_state: dict,
    *,
    initial_state_meta: MetaData | None = None,
    max_exec_steps: int = 20,
    node_functions: dict[str, Callable] | None = None,
    internal_node_mapping: dict[str, str] | None = None,
    timeout: float = 300.0,
    # Sequrity overrides
    llm_api_key: str | None | _NotGiven = NOT_GIVEN,
    features: FeaturesHeader | None | _NotGiven = NOT_GIVEN,
    security_policy: SecurityPolicyHeader | None | _NotGiven = NOT_GIVEN,
    fine_grained_config: FineGrainedConfigHeader | None | _NotGiven = NOT_GIVEN,
    provider: LlmServiceProvider | LlmServiceProviderStr | None | _NotGiven = NOT_GIVEN,
) -> dict:
    """Execute a LangGraph StateGraph through Sequrity's secure runtime.

    Args:
        transport: The sync transport layer.
        model: The LLM model identifier for agent nodes.
        graph: A LangGraph StateGraph instance.
        initial_state: Initial state dictionary.
        initial_state_meta: Optional metadata for the initial state.
        max_exec_steps: Maximum number of execution steps.
        node_functions: Custom node function implementations.
        internal_node_mapping: Mapping for internal node names.
        timeout: Timeout in seconds for each API request.
        llm_api_key: LLM provider API key override.
        features: Security features override.
        security_policy: Security policy override.
        fine_grained_config: Fine-grained config override.
        provider: LLM service provider override.

    Returns:
        Dictionary containing the final state.

    Raises:
        ValueError: If configuration is invalid for LangGraph execution.
        RuntimeError: If graph execution fails or times out.
    """
    # Resolve overrides to effective values
    eff_features = _resolve(features, transport._config.features)
    eff_fine_grained = _resolve(fine_grained_config, transport._config.fine_grained_config)

    # Validate configuration
    if eff_features is None or getattr(eff_features, "agent_arch", None) != "dual-llm":
        raise ValueError("LangGraph execution requires 'dual-llm' agent architecture.")
    if eff_fine_grained is None:
        raise ValueError("LangGraph execution requires 'fine_grained_config' to be provided.")
    if eff_fine_grained.response_format and eff_fine_grained.response_format.strip_response_content:
        raise ValueError("LangGraph execution requires 'strip_response_content' to be False.")
    if eff_fine_grained.fsm is None or eff_fine_grained.fsm.disable_rllm is not True:
        if eff_fine_grained.fsm is None:
            eff_fine_grained.fsm = FsmOverrides(disable_rllm=True)
        else:
            eff_fine_grained.fsm.disable_rllm = True

    # Determine provider and REST API type
    eff_provider = _resolve(provider, transport._config.provider)
    rest_api_type = RestApiType.MESSAGES if eff_provider == "anthropic" else RestApiType.CHAT_COMPLETIONS

    executor = LangGraphExecutor(
        graph=graph,
        node_functions=node_functions,
        internal_node_mapping=internal_node_mapping,
    )
    tools = executor.build_tool_definitions(rest_api_type)

    if initial_state_meta is None:
        initial_state_meta = MetaData(producers=set(), consumers={"*"}, tags=set())

    context_vars = {"initial_state": ValueWithMeta(value=initial_state, meta=initial_state_meta)}

    messages: list[dict] = [
        {
            "role": "user",
            "content": f"Execute the LangGraph StateGraph with initial_state: {json.dumps(initial_state, default=str)}.",
        }
    ]

    url = transport.build_url(rest_api_type, provider=provider, endpoint_type=EndpointType.LANGGRAPH)

    # Pre-resolve header values (constant across steps)
    eff_llm_key = _resolve(llm_api_key, transport._config.llm_api_key)
    eff_policy = _resolve(security_policy, transport._config.security_policy)

    def _build_headers(session_id: str | None = None) -> dict[str, str]:
        return build_sequrity_headers(
            api_key=transport._api_key,
            llm_api_key=eff_llm_key,
            features=eff_features.dump_for_headers(mode="json_str") if eff_features else None,
            policy=eff_policy.dump_for_headers(mode="json_str") if eff_policy else None,
            config=eff_fine_grained.dump_for_headers(mode="json_str") if eff_fine_grained else None,
            session_id=session_id,
        )

    current_state = initial_state.copy()
    loop_fn = _run_messages_loop if rest_api_type == RestApiType.MESSAGES else _run_chat_completions_loop
    return loop_fn(
        transport,
        executor,
        url=url,
        model=model,
        tools=tools,
        messages=messages,
        current_state=current_state,
        context_vars=context_vars,
        max_exec_steps=max_exec_steps,
        timeout=timeout,
        build_headers=_build_headers,
        session_id=None,
    )
