"""
LangGraph Integration with Sequrity Control API

This example demonstrates how to use LangGraph with Sequrity's compile_and_run_langgraph
to create a secure SQL agent with conditional routing.
"""

import os
from typing import Literal, TypedDict

from sequrity_api import SequrityClient
from sequrity_api.types.control.headers import (
    FeaturesHeader,
    FineGrainedConfigHeader,
    SecurityPolicyHeader,
)

# Try to import rich for better output formatting
try:
    from rich import print as rprint
except ImportError:
    rprint = print

# Check for LangGraph availability
try:
    from langgraph.graph import END, START, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    rprint("⚠️  LangGraph is not installed. Please install it with: pip install langgraph")
    exit(1)

# Initialize Sequrity client
openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
sequrity_api_key = os.getenv("SEQURITY_API_KEY", "your-sequrity-api-key")
base_url = os.getenv("SEQURITY_BASE_URL", None)

assert openrouter_api_key != "your-openrouter-api-key", "Please set your OPENROUTER_API_KEY environment variable."
assert sequrity_api_key != "your-sequrity-api-key", "Please set your SEQURITY_API_KEY environment variable."

client = SequrityClient(api_key=sequrity_api_key, base_url=base_url)


# Define the state schema for the SQL agent
class SQLAgentState(TypedDict):
    """State for SQL agent workflow

    Attributes:
        query: User's natural language query
        tables: Available database tables
        schema: Database schema information
        sql_query: Generated SQL query
        result: Query execution result
        needs_validation: Flag indicating if query needs validation
    """

    query: str
    tables: str
    schema: str
    sql_query: str
    result: str
    needs_validation: bool


# Define node functions for the workflow
def list_tables(state: SQLAgentState) -> dict:
    """List available database tables

    In a real application, this would query the database metadata.
    For this demo, we return a static list of tables.
    """
    rprint("📋 Listing available tables...")
    return {"tables": "users, orders, products"}


def get_schema(state: SQLAgentState) -> dict:
    """Get schema information for tables

    In a real application, this would retrieve actual schema from the database.
    For this demo, we return a simplified schema.
    """
    rprint(f"🔍 Getting schema for tables: {state['tables']}")
    schema_info = f"Schema for {state['tables']}: users(id, name, email), orders(id, user_id, total, date), products(id, name, price)"
    return {"schema": schema_info}


def generate_query(state: SQLAgentState) -> dict:
    """Generate SQL query based on user question

    In a real application, this might use an LLM to generate the query.
    For this demo, we create a simple query based on the user's input.
    """
    rprint(f"⚙️  Generating SQL for query: {state['query']}")

    # Simple query generation logic (in production, you'd use an LLM here)
    query_lower = state["query"].lower()
    if "user" in query_lower or "customer" in query_lower:
        sql = "SELECT * FROM users WHERE name LIKE '%recent%'"
    elif "order" in query_lower:
        sql = (
            "SELECT u.name, o.total, o.date FROM users u JOIN orders o ON u.id = o.user_id WHERE o.date > '2024-01-01'"
        )
    else:
        sql = "SELECT * FROM users"

    # Determine if query needs validation (complex queries)
    needs_validation = len(sql) > 50 or "JOIN" in sql

    return {"sql_query": sql, "needs_validation": needs_validation}


def validate_query(state: SQLAgentState) -> dict:
    """Validate and potentially modify the generated SQL query

    This adds safety measures like query limits.
    """
    rprint("✅ Validating SQL query...")
    validated_sql = state["sql_query"]

    # Add LIMIT if not present
    if "LIMIT" not in validated_sql.upper():
        validated_sql += " LIMIT 100"

    return {"sql_query": validated_sql, "needs_validation": False}


def execute_query(state: SQLAgentState) -> dict:
    """Execute the SQL query

    In a real application, this would execute against a real database.
    For this demo, we simulate execution and return mock results.
    """
    rprint(f"🚀 Executing SQL: {state['sql_query']}")

    # Simulate query execution
    result = f"Query executed successfully!\n\nSQL: {state['sql_query']}\n\nResults: Found 3 matching records:\n  1. John Doe (john@example.com)\n  2. Jane Smith (jane@example.com)\n  3. Bob Johnson (bob@example.com)"

    return {"result": result}


def route_validation(state: SQLAgentState) -> Literal["validate_query", "execute_query"]:
    """Conditional routing: decide whether query needs validation

    This function determines the next node based on the state.
    If the query needs validation, route to validate_query node.
    Otherwise, proceed directly to execute_query.
    """
    if state.get("needs_validation", False):
        rprint("⚠️  Query requires validation, routing to validate_query")
        return "validate_query"
    else:
        rprint("✓ Query looks safe, routing directly to execute_query")
        return "execute_query"


# Build the LangGraph workflow
def build_sql_agent_graph():
    """Construct the SQL agent workflow graph"""
    graph = StateGraph(SQLAgentState)

    # Add all workflow nodes
    graph.add_node("list_tables", list_tables)
    graph.add_node("get_schema", get_schema)
    graph.add_node("generate_query", generate_query)
    graph.add_node("validate_query", validate_query)
    graph.add_node("execute_query", execute_query)

    # Build the workflow edges
    graph.add_edge(START, "list_tables")
    graph.add_edge("list_tables", "get_schema")
    graph.add_edge("get_schema", "generate_query")

    # Conditional edge: route based on needs_validation
    graph.add_conditional_edges(
        "generate_query", route_validation, {"validate_query": "validate_query", "execute_query": "execute_query"}
    )

    graph.add_edge("validate_query", "execute_query")
    graph.add_edge("execute_query", END)

    return graph


# Main execution
if __name__ == "__main__":
    rprint("\n" + "=" * 70)
    rprint("🤖 SQL Agent with LangGraph + Sequrity Control API")
    rprint("=" * 70 + "\n")

    # Build the graph
    graph = build_sql_agent_graph()

    # Define initial state
    initial_state: SQLAgentState = {
        "query": "Find all users with recent orders",
        "tables": "",
        "schema": "",
        "sql_query": "",
        "result": "",
        "needs_validation": False,
    }

    # Prepare node functions dictionary
    # Note: Include routing functions (route_validation) as well as node functions
    node_functions = {
        "list_tables": list_tables,
        "get_schema": get_schema,
        "generate_query": generate_query,
        "validate_query": validate_query,
        "execute_query": execute_query,
        "route_validation": route_validation,  # Routing function for conditional edges
    }

    # Configure security features
    features = FeaturesHeader.create_dual_llm_headers()
    security_policy = SecurityPolicyHeader.create_default()
    fine_grained_config = FineGrainedConfigHeader(max_n_turns=10, disable_rllm=True)

    rprint(f"📝 User query: {initial_state['query']}\n")
    rprint("🔄 Running workflow with Sequrity Control API...\n")

    # Execute the graph with Sequrity
    result = client.control.compile_and_run_langgraph(
        model="openai/gpt-5-mini",
        llm_api_key=openrouter_api_key,
        graph=graph,
        initial_state=initial_state,
        service_provider="openrouter",
        node_functions=node_functions,
        max_exec_steps=30,
        features=features,
        security_policy=security_policy,
        fine_grained_config=fine_grained_config,
    )

    # Display results
    rprint("\n" + "=" * 70)
    rprint("✨ Workflow Completed!")
    rprint("=" * 70 + "\n")

    rprint("📊 Final State:")
    rprint(f"  • Tables: {result['tables']}")
    rprint(f"  • SQL Query: {result['sql_query']}")
    rprint(f"  • Result:\n{result['result']}")

    rprint("\n✅ Success! The SQL agent workflow executed securely through Sequrity.\n")
