from typing import Literal, TypedDict

import pytest

from sequrity_api import client
from sequrity_api.control.langgraph.graph_executor import LangGraphExecutor
from sequrity_api.service_provider import LlmServiceProviderEnum
from sequrity_api.types.control.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader
from sequrity_api_unittest.config import get_test_config

try:
    from langgraph.graph import StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


# Define state and node functions for testing
class SimpleState(TypedDict):
    """Simple state for testing"""

    query: str
    result: str


class SQLAgentState(TypedDict):
    """State for SQL agent example"""

    query: str
    tables: str
    schema: str
    sql_query: str
    result: str
    needs_validation: bool


def read_file(state: SimpleState) -> dict:
    """Read a file (external node)"""
    return {"result": "File contents: Hello World"}


def send_email(state: SimpleState) -> dict:
    """Send email (external node)"""
    return {"result": f"Email sent: {state['result']}"}


# SQL Agent nodes
def list_tables(state: SQLAgentState) -> dict:
    """List available database tables"""
    return {"tables": "users, orders, products"}


def get_schema(state: SQLAgentState) -> dict:
    """Get schema for tables"""
    schema_info = f"Schema for {state['tables']}: users(id, name), orders(id, user_id, total)"
    return {"schema": schema_info}


def generate_query(state: SQLAgentState) -> dict:
    """Generate SQL query based on user question"""
    # Simulate query generation
    sql = f"SELECT * FROM users WHERE name LIKE '%{state['query']}%'"
    needs_validation = len(sql) > 50  # Simple validation rule
    return {"sql_query": sql, "needs_validation": needs_validation}


def validate_query(state: SQLAgentState) -> dict:
    """Validate the generated SQL query"""
    validated_sql = state["sql_query"] + " LIMIT 100"  # Add safety limit
    return {"sql_query": validated_sql, "needs_validation": False}


def execute_query(state: SQLAgentState) -> dict:
    """Execute the SQL query"""
    result = f"Query executed: {state['sql_query']} -> Found 3 results"
    return {"result": result}


def route_validation(state: SQLAgentState) -> str:
    """Decide whether query needs validation"""
    if state.get("needs_validation", False):
        return "validate_query"
    else:
        return "execute_query"


class TestLangGraphCompilationAndExecution:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = client.SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url
        )

    @pytest.mark.skipif(not LANGGRAPH_AVAILABLE, reason="LangGraph is not installed")
    def test_graph_executor(self):
        from langgraph.graph import END, START, StateGraph

        graph = StateGraph(SimpleState)
        graph.add_node("read_file", read_file)
        graph.add_node("send_email", send_email)
        graph.add_edge(START, "read_file")
        graph.add_edge("read_file", "send_email")
        graph.add_edge("send_email", END)

        executor = LangGraphExecutor(graph=graph, node_functions={"read_file": read_file, "send_email": send_email})
        assert executor.generated_code is not None, "Generated code should not be None"
        generated_code = executor.generated_code
        assert "state = initial_state" in generated_code, "Should initialize state from initial_state"
        assert "read_file(state=state)" in generated_code, "Should call read_file with keyword argument"
        assert "send_email(state=state)" in generated_code, "Should call send_email with keyword argument"
        assert "final_return_value" in generated_code, "Should extract final return value"

        # Verify node functions are registered
        assert "read_file" in executor.node_functions
        assert "send_email" in executor.node_functions

        # Verify external nodes are identified
        assert "read_file" in executor.external_nodes
        assert "send_email" in executor.external_nodes

    @pytest.mark.skipif(not LANGGRAPH_AVAILABLE, reason="LangGraph is not installed")
    @pytest.mark.parametrize("service_provider", list(LlmServiceProviderEnum))
    def test_minimal(self, service_provider: LlmServiceProviderEnum):
        from langgraph.graph import END, START, StateGraph

        graph = StateGraph(SimpleState)
        graph.add_node("read_file", read_file)
        graph.add_node("send_email", send_email)
        graph.add_edge(START, "read_file")
        graph.add_edge("read_file", "send_email")
        graph.add_edge("send_email", END)

        initial_state = {"query": "Read the document", "result": ""}
        features = FeaturesHeader.create_dual_llm_headers()
        policy = SecurityPolicyHeader.create_default()
        config = FineGrainedConfigHeader(max_n_turns=10, disable_rllm=True)

        result = self.sequrity_client.control.compile_and_run_langgraph(
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            graph=graph,
            initial_state=initial_state,
            service_provider=service_provider,
            max_exec_steps=20,
            features=features,
            security_policy=policy,
            fine_grained_config=config,
            node_functions={"read_file": read_file, "send_email": send_email},
        )

        assert result is not None, "Result should not be None"
        assert isinstance(result, dict), "Result should be a dictionary"

        # Verify result contains expected keys from SimpleState
        assert "query" in result, "Result should contain 'query' key"
        assert "result" in result, "Result should contain 'result' key"

        # Verify the graph execution modified the state
        # At minimum, the read_file node should have updated the result
        assert result["result"] != "", f"Result should be updated by graph execution, got: {result['result']}"

        # The result should contain content from at least one of the nodes
        # Either "File contents:" from read_file or "Email sent:" from send_email
        assert "File contents:" in result["result"] or "Email sent:" in result["result"], (
            f"Result should contain output from graph nodes, got: {result['result']}"
        )

    @pytest.mark.skipif(not LANGGRAPH_AVAILABLE, reason="LangGraph is not installed")
    @pytest.mark.parametrize("service_provider", list(LlmServiceProviderEnum))
    def test_sql_agent_with_conditional_routing(self, service_provider: LlmServiceProviderEnum):
        from langgraph.graph import END, START, StateGraph

        graph = StateGraph(SQLAgentState)

        # Add all nodes
        graph.add_node("list_tables", list_tables)
        graph.add_node("get_schema", get_schema)
        graph.add_node("generate_query", generate_query)
        graph.add_node("validate_query", validate_query)
        graph.add_node("execute_query", execute_query)

        # Build the workflow
        graph.add_edge(START, "list_tables")
        graph.add_edge("list_tables", "get_schema")
        graph.add_edge("get_schema", "generate_query")

        # Conditional edge: route based on needs_validation
        graph.add_conditional_edges(
            "generate_query", route_validation, {"validate_query": "validate_query", "execute_query": "execute_query"}
        )

        graph.add_edge("validate_query", "execute_query")
        graph.add_edge("execute_query", END)

        node_functions = {
            "list_tables": list_tables,
            "get_schema": get_schema,
            "generate_query": generate_query,
            "validate_query": validate_query,
            "execute_query": execute_query,
        }
        initial_state = {
            "query": "Find all users with recent orders",
            "tables": "",
            "schema": "",
            "sql_query": "",
            "result": "",
            "needs_validation": False,
        }
        features = FeaturesHeader.create_dual_llm_headers()
        policy = SecurityPolicyHeader.create_default()
        config = FineGrainedConfigHeader(max_n_turns=10, disable_rllm=True)

        result = self.sequrity_client.control.compile_and_run_langgraph(
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            graph=graph,
            initial_state=initial_state,
            service_provider=service_provider,
            node_functions=node_functions,
            max_exec_steps=30,
            features=features,
            security_policy=policy,
            fine_grained_config=config,
        )

        # Verify execution
        assert result is not None, "Result should not be None"
        assert isinstance(result, dict), "Result should be a dictionary"

        # Verify state contains expected keys
        assert "tables" in result, "Result should have tables key"
        assert "schema" in result, "Result should have schema key"
        assert "sql_query" in result, "Result should have sql_query key"
        assert "result" in result, "Result should have result key"

        # Verify at least some nodes executed and updated state
        # Check if any of the pipeline steps produced output
        state_updated = (
            result["tables"] != "" or result["schema"] != "" or result["sql_query"] != "" or result["result"] != ""
        )
        assert state_updated, f"At least one node should have updated the state, got: {result}"

        # If sql_query was generated, verify it contains expected content
        if result["sql_query"]:
            assert "SELECT" in result["sql_query"], f"SQL query should be valid SQL, got: {result['sql_query']}"

        # If result was populated, verify it contains execution info
        if result["result"]:
            assert len(result["result"]) > 0, f"Result should contain execution information, got: {result['result']}"
