"""Control API wrapper module.

This module provides the ControlApiWrapper class for interacting with
Sequrity's Control API endpoints.
"""

from typing import TYPE_CHECKING, Callable, Literal

import httpx

from ..service_provider import LlmServiceProviderEnum
from ..types.chat_completion.request import Message, ReasoningEffort, ResponseFormat, Tool
from ..types.chat_completion.response import ChatCompletionResponse
from ..types.control.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader
from ..types.control.value_with_meta import MetaData
from .chat_completion import create_chat_completion_sync
from .langgraph import run_graph_sync

if TYPE_CHECKING:
    try:
        from langgraph.graph import StateGraph
    except ImportError:
        pass


class ControlApiWrapper:
    """Wrapper for Sequrity's Control API operations.

    The ControlApiWrapper provides methods for secure chat completions and
    LangGraph integration with Sequrity's security policies.

    Attributes:
        client: The underlying httpx client for HTTP requests.
        base_url: The base URL of the Sequrity API.
        sqrt_api_key: The Sequrity API key for authentication.
    """

    def __init__(self, client: httpx.Client, base_url: str, api_key: str):
        """Initialize the Control API wrapper.

        Args:
            client: An httpx.Client instance for making HTTP requests.
            base_url: The base URL of the Sequrity API.
            api_key: The Sequrity API key for authentication.
        """
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
        """Send a chat completion request through Sequrity's Control API.

        This method sends chat messages to an LLM provider while applying
        Sequrity's security features and policies.

        Args:
            messages: List of chat messages in the conversation.
            model: The LLM model identifier (e.g., "gpt-4o", "claude-3-opus").
            llm_api_key: API key for the LLM provider. Required unless using
                Sequrity's managed credits.
            features: Security features configuration including LLM mode
                (Single/Dual LLM), taggers, and constraints.
            security_policy: Security policy configuration specifying the
                policy language and rules.
            fine_grained_config: Advanced configuration options for session
                behavior and response formatting.
            service_provider: The LLM service provider to use. Defaults to
                auto-detection based on the model.
            session_id: Optional session identifier for conversation continuity.
            reasoning_effort: Reasoning effort level for supported models.
            response_format: Response format specification.
            seed: Random seed for reproducible outputs.
            stream: Whether to stream the response.
            temperature: Sampling temperature for the LLM.
            tools: List of tools available to the model.
            top_p: Top-p sampling parameter.
            return_type: Return format - "python" for ChatCompletionResponse
                object, "json" for raw dictionary.

        Returns:
            ChatCompletionResponse object or dictionary depending on return_type.

        Example:
            ```python
            from sequrity_api import SequrityClient
            from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader

            client = SequrityClient(api_key="your-sequrity-api-key")

            features = FeaturesHeader.create_single_llm_headers()
            security_policy = SecurityPolicyHeader.create_default()


            response = client.control.create_chat_completion(
                messages=[{"role": "user", "content": "Hello!"}],
                model="openai/gpt-5-mini",
                llm_api_key="your-openrouter-key",
                features=features,
                security_policy=security_policy,
                service_provider="openrouter",
            )
            ```
        """
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

    def compile_and_run_langgraph(
        self,
        model: str,
        llm_api_key: str | None,
        graph: "StateGraph",
        initial_state: dict,
        initial_state_meta: MetaData | None = None,
        max_exec_steps: int = 20,
        features: FeaturesHeader | None = None,
        security_policy: SecurityPolicyHeader | None = None,
        fine_grained_config: FineGrainedConfigHeader | None = None,
        service_provider: LlmServiceProviderEnum = LlmServiceProviderEnum.OPENROUTER,
        node_functions: dict[str, Callable] | None = None,
        internal_node_mapping: dict[str, str] | None = None,
    ) -> dict:
        """Compile and execute a LangGraph StateGraph with Sequrity security.

        This method takes a LangGraph StateGraph definition, compiles it, and
        executes it through Sequrity's secure runtime with policy enforcement.

        Args:
            model: The LLM model identifier for agent nodes.
            llm_api_key: API key for the LLM provider.
            graph: A LangGraph StateGraph instance defining the agent workflow.
            initial_state: Initial state dictionary to start graph execution.
            initial_state_meta: Optional metadata for the initial state.
            max_exec_steps: Maximum number of execution steps. Defaults to 20.
            features: Security features configuration.
            security_policy: Security policy configuration.
            fine_grained_config: Advanced configuration options.
            service_provider: The LLM service provider. Defaults to OPENROUTER.
            node_functions: Custom node function implementations.
            internal_node_mapping: Mapping for internal node names.

        Returns:
            Dictionary containing the final state and execution results.

        Example:
            ```python
            from langgraph.graph import StateGraph
            from sequrity_api import SequrityClient
            from sequrity_api.types.control.headers import FeaturesHeader

            client = SequrityClient(api_key="your-sequrity-api-key")
            features = FeaturesHeader.create_dual_llm_headers()
            security_policy = SecurityPolicyHeader.create_default()


            # Define your graph
            graph = StateGraph(...)
            ...

            def read_fine_func(doc_id: str) -> str: ...

            result = client.control.compile_and_run_langgraph(
                model="openai/gpt-5-mini",
                llm_api_key="your-openrouter-key",
                graph=graph,
                initial_state={"query": "Read the document", "result": ""},
                service_provider="openrouter",
                max_exec_steps=20,
                features=features,
                security_policy=security_policy,
                node_functions={"read_file": read_fine_func},
            )
            ```
        """
        return run_graph_sync(
            client=self.client,
            base_url=self.base_url,
            api_key=self.sqrt_api_key,
            model=model,
            llm_api_key=llm_api_key,
            graph=graph,
            initial_state=initial_state,
            initial_state_meta=initial_state_meta,
            max_exec_steps=max_exec_steps,
            features=features,
            security_policy=security_policy,
            fine_grained_config=fine_grained_config,
            service_provider=service_provider,
            node_functions=node_functions,
            internal_node_mapping=internal_node_mapping,
        )
