"""LangGraph StateGraph to code compiler.

This module converts LangGraph StateGraph definitions into executable
Python code and maps nodes to tool definitions.
"""

import json
from typing import Callable

from ....types.enums import RestApiType

try:
    from langgraph.graph import END, START, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class LangGraphExecutor:
    """Executor for running LangGraph StateGraphs through Sequrity.

    This class handles:
        1. Converting LangGraph to executable Python code
        2. Mapping nodes to tools (external) or internal functions
        3. Executing code via secure orchestrator
        4. Handling tool calls for external nodes
    """

    def __init__(
        self,
        graph: "StateGraph",
        node_functions: dict[str, Callable] | None = None,
        internal_node_mapping: dict[str, str] | None = None,
    ):
        """Initialize the executor.

        Args:
            graph: LangGraph StateGraph to execute.
            node_functions: Dict mapping node names to their functions.
            internal_node_mapping: Map of node names to internal tool names
                (e.g., {"agent": "parse_with_ai"}).

        Raises:
            RuntimeError: If LangGraph is not installed.
        """
        if not LANGGRAPH_AVAILABLE:
            raise RuntimeError("LangGraph is not installed. Install it with: pip install langgraph")

        self.graph = graph

        # Extract node functions if not provided
        if node_functions is None:
            self.node_functions = self._extract_function_map(graph)
        else:
            self.node_functions = node_functions

        # Determine which nodes are internal vs external
        self.internal_node_mapping = internal_node_mapping or {}
        self.external_nodes: set[str] = set()
        for node_name in self.node_functions.keys():
            if node_name not in self.internal_node_mapping:
                self.external_nodes.add(node_name)

        # Generate code once at initialization
        self.generated_code = self._graph_to_code(graph, self.node_functions)

    def _extract_function_map(self, graph: "StateGraph") -> dict[str, Callable]:
        """Extract node functions from LangGraph StateGraph."""
        function_map = {}

        if hasattr(graph, "nodes"):
            for node_name, node_data in graph.nodes.items():
                if hasattr(node_data, "func"):
                    function_map[node_name] = node_data.func
                elif callable(node_data):
                    function_map[node_name] = node_data

        return function_map

    def build_tool_definitions(self, rest_api_type: RestApiType = RestApiType.CHAT_COMPLETIONS) -> list[dict]:
        """Build tool definitions for external nodes.

        Args:
            rest_api_type: The REST API type determining the tool definition format.
                ``CHAT_COMPLETIONS`` produces OpenAI-style definitions.
                ``MESSAGES`` produces Anthropic-style definitions.

        Returns:
            List of tool definition dicts in the appropriate format.
        """
        tools = []

        for node_name in self.external_nodes:
            func = self.node_functions.get(node_name)
            description = (
                getattr(func, "__doc__", f"Execute node: {node_name}") if func else f"Execute node: {node_name}"
            )

            parameters = {
                "type": "object",
                "properties": {"state": {"type": "object", "description": "Current state dict"}},
                "required": ["state"],
            }

            if rest_api_type == RestApiType.MESSAGES:
                tool_def = {
                    "name": node_name,
                    "description": description,
                    "input_schema": parameters,
                }
            else:
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": node_name,
                        "description": description,
                        "parameters": parameters,
                    },
                }
            tools.append(tool_def)

        return tools

    def execute_tool_call(self, tool_call: dict, rest_api_type: RestApiType = RestApiType.CHAT_COMPLETIONS) -> dict:
        """Execute a tool call (external node).

        Args:
            tool_call: Tool call dict. Format depends on ``rest_api_type``:
                - ``CHAT_COMPLETIONS``: ``{"function": {"name": ..., "arguments": ...}}``
                - ``MESSAGES``: ``{"name": ..., "input": {...}}``
            rest_api_type: The REST API type determining the tool call format.

        Returns:
            The result dict from executing the node function.

        Raises:
            RuntimeError: If no function is found for the specified tool name.
        """
        if rest_api_type == RestApiType.MESSAGES:
            tool_name = tool_call.get("name")
            arguments = tool_call.get("input", {})
        else:
            tool_name = tool_call.get("function", {}).get("name")
            arguments_str = tool_call.get("function", {}).get("arguments", "{}")
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                arguments = {}

        if not tool_name:
            raise RuntimeError("Tool call missing tool name")

        node_func = self.node_functions.get(tool_name)
        if not node_func:
            raise RuntimeError(f"No function found for external node: {tool_name}")

        state = arguments.get("state", {})
        result = node_func(state)

        return result

    def _graph_to_code(self, graph: "StateGraph", function_map: dict[str, Callable]) -> str:
        """Convert a LangGraph StateGraph into executable Python code."""
        nodes = graph.nodes
        edges = list(graph.edges)
        branches = dict(graph.branches)

        code_lines = []
        code_lines.append("# Module-level code - assumes initial_state is predefined")
        code_lines.append("state = initial_state")
        code_lines.append("")

        start_edges = [target for source, target in edges if source == START]
        if not start_edges:
            code_lines.append("# Extract final result for user")
            code_lines.append("final_return_value = state.get('result', state)")
            return "\n".join(code_lines)

        visited = set()
        self._generate_node_code(start_edges[0], nodes, edges, branches, function_map, code_lines, visited, indent=0)

        code_lines.append("")
        code_lines.append("# Extract final result for user")
        code_lines.append("final_return_value = state.get('result', state)")

        return "\n".join(code_lines)

    def _generate_node_code(self, node_name, nodes, edges, branches, function_map, code_lines, visited, indent=0):
        """Recursively generate code for a node and its successors."""
        if node_name in visited or node_name == END or node_name == "__end__":
            return

        visited.add(node_name)
        indent_str = "    " * indent

        node_spec = nodes.get(node_name)
        if not node_spec:
            return

        node_func = node_spec.runnable
        if function_map and node_name in function_map:
            func_name = function_map[node_name].__name__
        else:
            func_name = getattr(node_func, "__name__", getattr(node_func, "name", str(node_name)))

        code_lines.append(f"{indent_str}# Node: {node_name}")
        code_lines.append(f"{indent_str}{node_name}_result = {func_name}(state=state)")
        code_lines.append(f"{indent_str}# Update state")
        code_lines.append(f"{indent_str}for key, value in {node_name}_result.items():")
        code_lines.append(f"{indent_str}    if key in state:")
        code_lines.append(f"{indent_str}        if isinstance(value, list) and isinstance(state[key], list):")
        code_lines.append(f"{indent_str}            state[key].extend(value)")
        code_lines.append(f"{indent_str}        else:")
        code_lines.append(f"{indent_str}            state[key] = value")
        code_lines.append(f"{indent_str}    else:")
        code_lines.append(f"{indent_str}        state[key] = value")
        code_lines.append("")

        if node_name in branches and branches[node_name]:
            branch_name = list(branches[node_name].keys())[0]
            branch_spec = branches[node_name][branch_name]
            condition_name = branch_name

            possible_next = set()
            if hasattr(branch_spec, "ends"):
                ends = branch_spec.ends
                possible_next.update(ends.values() if isinstance(ends, dict) else ends)

            for source, target in edges:
                if source == node_name and target not in (END, "__end__"):
                    possible_next.add(target)

            code_lines.append(f"{indent_str}# Conditional routing")
            code_lines.append(f"{indent_str}next_node = {condition_name}(state=state)")
            code_lines.append("")

            if possible_next:
                first = True
                for next_node in sorted(possible_next):
                    if_keyword = "if" if first else "elif"
                    first = False

                    code_lines.append(f"{indent_str}{if_keyword} next_node == '{next_node}':")
                    branch_visited = visited.copy()
                    self._generate_node_code(
                        next_node, nodes, edges, branches, function_map, code_lines, branch_visited, indent + 1
                    )
        else:
            next_nodes = [target for source, target in edges if source == node_name]
            if next_nodes and next_nodes[0] != END and next_nodes[0] != "__end__":
                self._generate_node_code(
                    next_nodes[0], nodes, edges, branches, function_map, code_lines, visited, indent
                )
