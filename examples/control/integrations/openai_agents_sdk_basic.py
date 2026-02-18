"""
Basic OpenAI Agents SDK integration example with Sequrity.

This example demonstrates how to use Sequrity with the OpenAI Agents SDK.
"""

import asyncio
import os

from sequrity.control import FeaturesHeader, SecurityPolicyHeader
from sequrity.control.integrations.openai_agents_sdk import (
    create_sequrity_openai_agents_sdk_client,
)


# --8<-- [start:basic-setup]
# Create Sequrity client
client = create_sequrity_openai_agents_sdk_client(
    sequrity_api_key=os.environ["SEQURITY_API_KEY"],
    features=FeaturesHeader.dual_llm(),
    security_policy=SecurityPolicyHeader.dual_llm(),
    service_provider="openrouter",
    llm_api_key=os.environ["OPENROUTER_API_KEY"],
)
# --8<-- [end:basic-setup]


# --8<-- [start:basic-completion]
async def basic_completion():
    """Simple chat completion example."""
    response = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": "What is 2 + 2? Answer briefly."}],
    )

    print(f"Response: {response.choices[0].message.content}")
    print(f"Session ID: {client.session_id}")


# --8<-- [end:basic-completion]


# --8<-- [start:session-management]
async def session_management():
    """Demonstrate session management."""
    # First request - establishes session
    messages = [{"role": "user", "content": "My name is Alice."}]
    response1 = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
    )
    print(f"First response: {response1.choices[0].message.content}")
    print(f"Session ID: {client.session_id}")

    # Add assistant response to message history
    messages.append({"role": "assistant", "content": response1.choices[0].message.content})

    # Second request - uses same session with full message history
    messages.append({"role": "user", "content": "What is my name?"})
    response2 = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
    )
    print(f"Second response: {response2.choices[0].message.content}")

    # Reset session for new conversation
    client.reset_session()
    print(f"Session ID after reset: {client.session_id}")


# --8<-- [end:session-management]


# --8<-- [start:with-agents-sdk]
async def with_agents_sdk():
    """Use with OpenAI Agents SDK."""
    try:
        from agents import Agent, RunConfig, Runner

        # Create an agent
        agent = Agent(
            name="ResearchAssistant",
            instructions="You are a helpful research assistant. Keep responses concise.",
        )

        # Configure agent to use Sequrity
        run_config = RunConfig(model="gpt-5-mini", model_provider=client)

        # Run the agent
        result = await Runner.run(
            agent,
            input="What are the main benefits of dual-LLM architecture?",
            run_config=run_config,
        )

        print(f"Agent response: {result.final_output}")
    except ImportError:
        print("OpenAI Agents SDK not installed. Skipping agent example.")


# --8<-- [end:with-agents-sdk]


async def main():
    """Run all examples."""
    print("=== Basic Completion ===")
    await basic_completion()

    # Reset session before next example
    client.reset_session()

    print("\n=== Session Management ===")
    await session_management()

    # Reset session before next example
    client.reset_session()

    print("\n=== With Agents SDK ===")
    await with_agents_sdk()


if __name__ == "__main__":
    asyncio.run(main())
