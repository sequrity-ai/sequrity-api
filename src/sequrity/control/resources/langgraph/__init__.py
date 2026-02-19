"""LangGraph resource — ``client.control.langgraph``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from ...._sentinel import NOT_GIVEN, _NotGiven
from ...._types.enums import LlmServiceProvider, LlmServiceProviderStr
from ..._transport import ControlSyncTransport
from ...types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader
from ...types.dual_llm_response import MetaData

if TYPE_CHECKING:
    from langgraph.graph import StateGraph


class LangGraphResource:
    """LangGraph execution — ``client.control.langgraph``."""

    def __init__(self, transport: ControlSyncTransport) -> None:
        self._transport = transport

    def run(
        self,
        graph: "StateGraph",
        initial_state: dict,
        model: str,
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
        """Compile and execute a LangGraph StateGraph with Sequrity security.

        Args:
            graph: A LangGraph StateGraph instance defining the agent workflow.
            initial_state: Initial state dictionary to start graph execution.
            model: The LLM model identifier for agent nodes.
            initial_state_meta: Optional metadata for the initial state.
            max_exec_steps: Maximum number of execution steps. Defaults to 20.
            node_functions: Custom node function implementations.
            internal_node_mapping: Mapping for internal node names.
            timeout: Timeout in seconds for each API request. Defaults to 300.0.
            llm_api_key: LLM provider API key override.
            features: Security features override.
            security_policy: Security policy override.
            fine_grained_config: Fine-grained config override.
            provider: LLM service provider override.

        Returns:
            Dictionary containing the final state and execution results.
        """
        from ._runner import run_graph_sync

        return run_graph_sync(
            transport=self._transport,
            model=model,
            graph=graph,
            initial_state=initial_state,
            initial_state_meta=initial_state_meta,
            max_exec_steps=max_exec_steps,
            node_functions=node_functions,
            internal_node_mapping=internal_node_mapping,
            timeout=timeout,
            llm_api_key=llm_api_key,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            provider=provider,
        )
