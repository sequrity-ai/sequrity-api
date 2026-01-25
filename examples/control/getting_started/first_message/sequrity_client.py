"""Getting Started with Sequrity Control API - Python Client Examples

Prerequisites:
- A Sequrity API key (from your dashboard at sequrity.ai)
- An LLM provider API key (e.g., OpenAI, OpenRouter)

Installation:
    pip install sequrity-api
"""

import os

# --8<-- [start:imports]
from sequrity_api import SequrityClient
from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader
# --8<-- [end:imports]

sequrity_api_key = os.getenv("SEQURITY_API_KEY", "your-sequrity-api-key")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key")

# =============================================================================
# Single-LLM
# =============================================================================
# Single-LLM passes your request directly to the LLM with optional
# security taggers and constraints.


# --8<-- [start:single_llm]
def single_llm_example():
    # Initialize the client
    client = SequrityClient(api_key=sequrity_api_key)

    # Create feature and policy headers
    features = FeaturesHeader.create_single_llm_headers()
    policy = SecurityPolicyHeader.create_default()

    # Send a chat completion request
    response = client.control.create_chat_completion(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini",  # model name from your LLM provider
        llm_api_key=openrouter_api_key,
        features=features,
        security_policy=policy,
        service_provider="openrouter",  # or "openai"
    )

    # Print the response
    print(response)
# --8<-- [end:single_llm]


# =============================================================================
# Dual-LLM
# =============================================================================
# Dual-LLM uses a planning LLM to generate secure execution plans on which
# security policies and features are enforced. This provides stronger security
# guarantees for agentic use cases.


# --8<-- [start:dual_llm]
def dual_llm_example():
    # Initialize the client
    client = SequrityClient(api_key=sequrity_api_key)

    # Create dual LLM feature headers
    features = FeaturesHeader.create_dual_llm_headers()
    policy = SecurityPolicyHeader.create_default()

    # Send a chat completion request
    response = client.control.create_chat_completion(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini",
        llm_api_key=openrouter_api_key,
        features=features,
        security_policy=policy,
    )

    print(response)
# --8<-- [end:dual_llm]


if __name__ == "__main__":
    print("=== Single LLM Mode ===")
    single_llm_example()

    print("\n=== Dual LLM Mode ===")
    dual_llm_example()
