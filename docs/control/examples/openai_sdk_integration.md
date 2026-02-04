# OpenAI Agents SDK Integration

This guide demonstrates how to use Sequrity with the [OpenAI Agent ADK](https://github.com/openai/openai-agents) framework.

## Overview

The `SequrityAsyncOpenAI` client is a drop-in replacement for OpenAI's `AsyncOpenAI` client that automatically adds Sequrity's security features:

- **Dual-LLM Architecture**: Separate planning and quarantined execution
- **Automatic Session Tracking**: Maintains conversation context across requests
- **Security Headers**: Automatically injects features, policies, and configuration
- **Full OpenAI Compatibility**: Works seamlessly with OpenAI Agent ADK

## Installation

```bash
# Install sequrity-api with OpenAI support (included by default)
pip install sequrity

# Optional: Install OpenAI Agent ADK for agent framework support
pip install openai-agents
```

## Basic Usage

```python
import asyncio
from agents import Agent, Runner, RunConfig
from sequrity.integrations import create_sequrity_openai_client
from sequrity.control.types.headers import FeaturesHeader, SecurityPolicyHeader

async def main():
    # Create Sequrity client
    client = create_sequrity_openai_client(
        sequrity_api_key="your-sequrity-api-key",
        features=FeaturesHeader.dual_llm(),
        security_policy=SecurityPolicyHeader.dual_llm()
    )

    # Create an agent
    agent = Agent(
        name="ResearchAssistant",
        instructions="You are a helpful research assistant."
    )

    # Configure agent to use Sequrity
    run_config = RunConfig(
        model="gpt-5-mini",
        model_provider=client
    )

    # Run the agent
    result = await Runner.run(
        agent,
        input="What are the main benefits of dual-LLM architecture?",
        run_config=run_config
    )

    print(result.final_output)

asyncio.run(main())
```

## Session Management

The client automatically tracks session IDs across requests for conversation continuity:

```python
import asyncio
from sequrity.integrations import create_sequrity_openai_client
from sequrity.control.types.headers import FeaturesHeader, SecurityPolicyHeader

async def main():
    client = create_sequrity_openai_client(
        sequrity_api_key="your-key",
        features=FeaturesHeader.dual_llm(),
        security_policy=SecurityPolicyHeader.dual_llm()
    )

    # First request - establishes session
    response1 = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": "My name is Alice."}]
    )
    print(f"Session ID: {client.session_id}")

    # Second request - uses same session
    response2 = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": "What is my name?"}]
    )
    print(response2.choices[0].message.content)  # Should mention Alice

    # Reset session for new conversation
    client.reset_session()
    print(f"Session ID after reset: {client.session_id}")  # None

asyncio.run(main())
```

## Security Configuration


```python
from sequrity.integrations import create_sequrity_openai_client
from sequrity.control.types.headers import (
    FeaturesHeader,
    SecurityPolicyHeader,
    FineGrainedConfigHeader
)

client = create_sequrity_openai_client(
    sequrity_api_key="your-key",
    features=FeaturesHeader.dual_llm(),
    security_policy=SecurityPolicyHeader.from_sqrt_code(
        """
        tool "search" {
            must allow if query not contains "password";
            must deny always;
        }

        tool "database" {
            must deny always;
        }
        """
    ),
    fine_grained_config=FineGrainedConfigHeader(
        max_n_turns=10,
        include_program=True  # Include execution program in response
    )
)
```

## See Also

- [FeaturesHeader Documentation](../reference/sequrity_client/headers/features_header.md)
- [SecurityPolicyHeader Documentation](../reference/sequrity_client/headers/policy_header.md)
- [FineGrainedConfigHeader Documentation](../reference/sequrity_client/headers/config_header.md)
- [OpenAI Agent ADK Documentation](https://github.com/openai/openai-agents)
