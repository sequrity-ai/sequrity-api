# LangGraph Integration with Sequrity Control API

This tutorial demonstrates how to integrate [LangGraph](https://langchain-ai.github.io/langgraph/) with Sequrity's Control API using the [`compile_and_run_langgraph`][sequrity_api.control.wrapper.ControlApiWrapper.compile_and_run_langgraph] method. We'll build a SQL agent with conditional routing that showcases LangGraph's powerful workflow capabilities while maintaining security through Sequrity.

## Prerequisites

Before starting, ensure you have:

- **Sequrity API Key**: Sign up at [Sequrity](https://sequrity.ai) to get your API key
- **LLM Provider API Key**: This example uses OpenRouter, but you can use any supported provider
- **LangGraph Installed**: Install via `pip install langgraph`

Set your API keys as environment variables:

```bash
export SEQURITY_API_KEY="your-sequrity-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

??? tip "Download Tutorial Script"

    - [Sequrity Client version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/langgraph/sequrity_client.py)

## Installation

Install the required packages:

```bash
pip install sequrity-api langgraph rich
```

The `rich` package is optional but provides nice formatted output.

## Why Use Sequrity with LangGraph?

When building LangGraph workflows, you often need:

1. **Security Controls**: Ensure your agent doesn't leak sensitive data or perform unauthorized actions
2. **Execution Monitoring**: Track and audit workflow execution for compliance
3. **LLM Integration**: Secure interaction with external LLM providers
4. **Policy Enforcement**: Apply fine-grained security policies to tool calls and data flow

Sequrity's [`compile_and_run_langgraph`][sequrity_api.control.wrapper.ControlApiWrapper.compile_and_run_langgraph] method provides all of this out-of-the-box, allowing you to focus on building your workflow logic while Sequrity handles security.

## Tutorial Overview: SQL Agent with Conditional Routing

We'll build a SQL agent that:

1. **Lists available database tables**
2. **Retrieves schema information**
3. **Generates SQL queries** based on user input
4. **Conditionally validates** complex queries
5. **Executes the query** and returns results

The workflow includes conditional routing: simple queries execute directly, while complex queries go through a validation step first.

## Step 1: Define the State Schema

LangGraph workflows are built around a typed state that flows through nodes. Let's define our SQL agent's state:

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:46:61"
```

Each node in the workflow can read from and update this state.

## Step 2: Implement Node Functions

### External Data Retrieval Nodes

These nodes represent external operations (e.g., database queries). In a real application, they would interact with actual databases:

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:64:85"
```

### Query Generation Node

This node generates SQL based on the user's natural language query:

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:87:110"
```

### Validation and Execution Nodes

These nodes handle query validation and execution:

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:112:139"
```

### Conditional Routing Function

This function determines the next node based on the current state:

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:140:154"
```

!!! note "Routing Functions Must Be Included"
    This routing function must be included in the `node_functions` dictionary when calling `compile_and_run_langgraph`, even though it's not a node. It's referenced by the conditional edge and needs to be available during execution.

## Step 3: Build the LangGraph Workflow

Now we construct the graph by connecting nodes and edges:

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:155:183"
```

### Understanding the Workflow

1. **START → list_tables**: Begin by listing available tables
2. **list_tables → get_schema**: Retrieve schema for those tables
3. **get_schema → generate_query**: Generate SQL based on user input and schema
4. **Conditional Branch**:
    - If `needs_validation=True`: → validate_query → execute_query → END
    - If `needs_validation=False`: → execute_query → END

This demonstrates LangGraph's powerful conditional routing capabilities.

## Step 4: Execute with Sequrity Control API

### Initialize the Sequrity Client

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:35:43"
```

### Configure Security Settings

Set up security features, policies, and configurations:

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:216:218"
```

- **Features**: Use Dual-LLM mode for enhanced security
- **Security Policy**: Apply default security policies (you can customize these with SQRT)
- **Fine-Grained Config**: Limit execution to 10 turns

### Prepare Initial State and Node Functions

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:194:213"
```

!!! important "Include Routing Functions"
    When your graph uses conditional edges (like `add_conditional_edges`), you **must** include the routing function in the `node_functions` dictionary. In this example, `route_validation` is the routing function that determines whether to go to `validate_query` or `execute_query`. Even though it's not a "node" in the traditional sense, it needs to be accessible during execution.

### Execute the Graph

Finally, call `compile_and_run_langgraph` to execute your workflow securely:

```python
--8<-- "examples/control/getting_started/langgraph/sequrity_client.py:223:251"
```

### Understanding the Parameters

- **`model`**: The LLM model to use (can specify separate models for PLLM and QLLM)
- **`llm_api_key`**: API key for your LLM provider
- **`graph`**: Your LangGraph StateGraph instance
- **`initial_state`**: Starting state for the workflow
- **`service_provider`**: LLM provider (e.g., "openrouter", "openai")
- **`node_functions`**: Dictionary mapping node names to their functions
- **`max_exec_steps`**: Maximum execution steps (prevents infinite loops)
- **`features`**: Security features configuration
- **`security_policy`**: Security policies in SQRT
- **`fine_grained_config`**: Additional configuration options


## Running the Example

Execute the example script and you should see output similar to:

```
======================================================================
🤖 SQL Agent with LangGraph + Sequrity Control API
======================================================================

📝 User query: Find all users with recent orders

🔄 Running workflow with Sequrity Control API...

📋 Listing available tables...
🔍 Getting schema for tables: users, orders, products
⚙️  Generating SQL for query: Find all users with recent orders
✓ Query looks safe, routing directly to execute_query
🚀 Executing SQL: SELECT * FROM users WHERE name LIKE '%recent%'

======================================================================
✨ Workflow Completed!
======================================================================

📊 Final State:
  • Tables: users, orders, products
  • SQL Query: SELECT * FROM users WHERE name LIKE '%recent%'
  • Result:
Query executed successfully!

SQL: SELECT * FROM users WHERE name LIKE '%recent%'

Results: Found 3 matching records:
  1. John Doe (john@example.com)
  2. Jane Smith (jane@example.com)
  3. Bob Johnson (bob@example.com)

✅ Success! The SQL agent workflow executed securely through Sequrity.
```

## Additional Customizations

### Custom Security Policies

You can define custom SQRT policies to restrict specific operations:

```python
security_policy = SecurityPolicyHeader(
    language="sqrt",
    codes=r"""
    // Prevent DELETE operations
    tool "execute_query" {
        hard deny when sql_query.value matching r".*DELETE.*";
    }

    // Tag sensitive table access
    let sensitive_tables = {"users", "payments"};
    tool "get_schema" {
        when tables.value overlaps sensitive_tables -> @tags |= {"sensitive"};
    }
    """
)
```

### Multi-LLM Configuration

Use different models for planning and execution:

```python
# Format: "pllm_model,qllm_model"
model = "openai/gpt-5-mini,anthropic/claude-sonnet-4.5"
```

### Error Handling

The workflow automatically handles errors, but you can add custom error handling in your nodes:

```python
def execute_query(state: SQLAgentState) -> dict:
    try:
        # Execute query logic
        result = execute_sql(state["sql_query"])
        return {"result": result}
    except Exception as e:
        return {"result": f"Error executing query: {str(e)}"}
```

