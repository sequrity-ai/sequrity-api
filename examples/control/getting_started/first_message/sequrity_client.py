"""Getting Started with Sequrity Control API - Python Client Examples

Prerequisites:
- A Sequrity API key (from your dashboard at sequrity.ai)
- An LLM provider API key (e.g., OpenAI, OpenRouter)

Installation:
    pip install sequrity
"""

# ---8<-- [start:imports_os]
import os

# ---8<-- [end:imports_os]
# --8<-- [start:imports_sequrity_client]
from sequrity import SequrityClient

# --8<-- [end:imports_sequrity_client]
# --8<-- [start:imports_headers]
from sequrity.control import FeaturesHeader, SecurityPolicyHeader

# --8<-- [end:imports_headers]

# --8<-- [start:api_keys]
sequrity_key = os.getenv("SEQURITY_API_KEY", "your-sequrity-api-key")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key")
# --8<-- [end:api_keys]

# =============================================================================
# First Message Example
# =============================================================================


# --8<-- [start:first_message]
def first_message_example():
    # Initialize the Sequrity client
    client = SequrityClient(api_key=sequrity_key)

    # Send a chat completion request
    response = client.control.create_chat_completion(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini",  # model name from your LLM provider
        llm_api_key=openrouter_api_key,  # your LLM provider API key
    )

    print(response)


# --8<-- [end:first_message]


# =============================================================================
# Single-LLM
# =============================================================================


# --8<-- [start:single_llm]
def single_llm_example():
    # Initialize the client
    client = SequrityClient(api_key=sequrity_key)

    # Create feature and policy headers
    features = FeaturesHeader.single_llm()
    policy = SecurityPolicyHeader.single_llm()

    # Send a chat completion request
    response = client.control.create_chat_completion(
        messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
        model="openai/gpt-5-mini",
        llm_api_key=openrouter_api_key,
        features=features,  # security features
        security_policy=policy,  # security policy
        service_provider="openrouter",
    )

    print(response)


# --8<-- [end:single_llm]


# =============================================================================
# Dual-LLM
# =============================================================================


# --8<-- [start:dual_llm]
def dual_llm_example():
    # Initialize the client
    client = SequrityClient(api_key=sequrity_key)

    # Create dual LLM feature headers
    features = FeaturesHeader.dual_llm()
    policy = SecurityPolicyHeader.dual_llm()

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

# --8<-- [start:main]
if __name__ == "__main__":
    # --8<-- [end:main]
    # <--8<-- [start:run_first_message]
    print("=== First Message Example ===")
    first_message_example()
    # <--8<-- [end:run_first_message]

    print("=== Single LLM Mode ===")
    single_llm_example()

    print("\n=== Dual LLM Mode ===")
    dual_llm_example()
