"""
Basic LangGraph integration example with Sequrity.

This example demonstrates how to use Sequrity with LangGraph for building
secure agent workflows.
"""

import os

from langchain_core.tools import tool
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from sequrity.control import FeaturesHeader, SecurityPolicyHeader
from sequrity.control.integrations.langgraph import create_sequrity_langgraph_client


# --8<-- [start:basic-setup]
# Create Sequrity LangGraph client
llm = create_sequrity_langgraph_client(
    sequrity_api_key=os.environ["SEQURITY_API_KEY"],
    features=FeaturesHeader.dual_llm(),
    security_policy=SecurityPolicyHeader.dual_llm(),
    service_provider="openrouter",
    llm_api_key=os.environ["OPENROUTER_API_KEY"],
    model="gpt-5-mini",
)
# --8<-- [end:basic-setup]


# --8<-- [start:define-tools]
@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Search results for: {query}"


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)  # noqa: S307
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


# --8<-- [end:define-tools]


# --8<-- [start:build-graph]
# Define state schema
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class State(TypedDict):
    """State for the agent."""

    messages: Annotated[list, add_messages]


# Bind tools to LLM
tools = [search, calculator]
llm_with_tools = llm.bind_tools(tools)


# Define chatbot node
def chatbot(state: State):
    """Chatbot node that calls the LLM."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools))
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Compile the graph
graph = graph_builder.compile()
# --8<-- [end:build-graph]


# --8<-- [start:run-graph]
def run_example():
    """Run the example."""
    from langchain_core.messages import HumanMessage

    # Run the graph
    events = graph.stream({"messages": [HumanMessage(content="Search for LangGraph and calculate 2+2")]})

    # Print results
    for event in events:
        for value in event.values():
            if "messages" in value:
                message = value["messages"][-1]
                print(f"\n{message.type}: {message.content}")


# --8<-- [end:run-graph]


if __name__ == "__main__":
    run_example()
