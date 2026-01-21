"""
LangGraph integration for SequrityClient

This module provides functionality to execute LangGraph StateGraphs securely
through the Sequrity orchestrator.
"""

import json
from typing import Callable

try:
    from langgraph.graph import END, START, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class LangGraphExecutor:
    """
    Executor for running LangGraph StateGraphs through Sequrity.

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
        """
        Initialize the executor.

        Args:
            graph: LangGraph StateGraph to execute
            node_functions: Dict mapping node names to their functions (optional)
            internal_node_mapping: Map of node names to internal tool names
                                  (e.g., {"agent": "parse_with_ai"})
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

        # Access internal graph structure to get nodes
        if hasattr(graph, "nodes"):
            for node_name, node_data in graph.nodes.items():
                if hasattr(node_data, "func"):
                    function_map[node_name] = node_data.func
                elif callable(node_data):
                    function_map[node_name] = node_data

        return function_map

    def build_tool_definitions(self) -> list[dict]:
        """
        Build OpenAI-style tool definitions for external nodes.

        Each external node becomes a tool that the orchestrator can call.
        """
        tools = []

        for node_name in self.external_nodes:
            func = self.node_functions.get(node_name)

            # Get description from function if available
            if func:
                description = getattr(func, "__doc__", f"Execute node: {node_name}")
            else:
                description = f"Execute node: {node_name}"

            # Build tool schema
            tool_def = {
                "type": "function",
                "function": {
                    "name": node_name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": {"state": {"type": "object", "description": "Current state dict"}},
                        "required": ["state"],
                    },
                },
            }
            tools.append(tool_def)

        return tools

    def execute_tool_call(self, tool_call: dict) -> dict:
        """
        Execute a tool call (external node).

        Args:
            tool_call: Tool call dict with id, name, arguments

        Returns:
            Tool result dict
        """
        tool_name = tool_call.get("function", {}).get("name")
        arguments_str = tool_call.get("function", {}).get("arguments", "{}")

        # Parse arguments
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            arguments = {}

        # Get the node function
        node_func = self.node_functions.get(tool_name)
        if not node_func:
            raise RuntimeError(f"No function found for external node: {tool_name}")

        # Execute the node function
        state = arguments.get("state", {})
        result = node_func(state)

        return result

    def _graph_to_code(self, graph: "StateGraph", function_map: dict[str, Callable]) -> str:
        """
        Convert a LangGraph StateGraph into executable Python code.

        Generates:
        - Module-level code with state = initial_state
        - Linear flow with if-else for conditional routing
        - Uses keyword arguments for function calls
        """
        nodes = graph.nodes
        edges = list(graph.edges)
        branches = dict(graph.branches)

        code_lines = []
        code_lines.append("# Module-level code - assumes initial_state is predefined")
        code_lines.append("state = initial_state")
        code_lines.append("")

        # Find starting node
        start_edges = [target for source, target in edges if source == START]
        if not start_edges:
            code_lines.append("# Extract final result for user")
            code_lines.append("final_return_value = state.get('result', state)")
            return "\n".join(code_lines)

        # Generate code for each node
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

        # Get function name
        node_spec = nodes.get(node_name)
        if not node_spec:
            return

        node_func = node_spec.runnable
        if function_map and node_name in function_map:
            func_name = function_map[node_name].__name__
        else:
            func_name = getattr(node_func, "__name__", getattr(node_func, "name", str(node_name)))

        # Generate node execution code with keyword arguments
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

        # Check for conditional edges
        if node_name in branches and branches[node_name]:
            # Has conditional routing
            branch_name = list(branches[node_name].keys())[0]
            branch_spec = branches[node_name][branch_name]

            # Use the branch name as the condition function name
            condition_name = branch_name

            # Get possible next nodes
            possible_next = set()
            if hasattr(branch_spec, "ends"):
                ends = branch_spec.ends
                possible_next.update(ends.values() if isinstance(ends, dict) else ends)

            # Also check edges
            for source, target in edges:
                if source == node_name and target not in (END, "__end__"):
                    possible_next.add(target)

            code_lines.append(f"{indent_str}# Conditional routing")
            code_lines.append(f"{indent_str}next_node = {condition_name}(state=state)")
            code_lines.append("")

            # Generate if-else for each possible path
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
            # Regular edge - no condition
            next_nodes = [target for source, target in edges if source == node_name]
            if next_nodes and next_nodes[0] != END and next_nodes[0] != "__end__":
                self._generate_node_code(
                    next_nodes[0], nodes, edges, branches, function_map, code_lines, visited, indent
                )
