# --8<-- [start:imports]
import os

import requests

from sequrity.control.types import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader
from sequrity.control.types.headers import FsmOverrides, PolicyCode, ResponseFormatOverrides

# --8<-- [end:imports]

# --8<-- [start:api_keys]
sequrity_key = os.getenv("SEQURITY_API_KEY", "your-sequrity-api-key")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
base_url = os.getenv("SEQURITY_BASE_URL", "https://api.sequrity.ai")
# --8<-- [end:api_keys]

# --8<-- [start:build_headers]
# Build each header using the Pydantic classes, then serialize for HTTP transport.
features = FeaturesHeader.dual_llm(pii_redaction=True, toxicity_filter=True)

security_policy = SecurityPolicyHeader(
    codes=PolicyCode(
        code=r"""
            let sensitive_docs = {"internal_use", "confidential"};
            tool "get_internal_document" -> @tags |= sensitive_docs;
            tool "send_email" {
                hard deny when (body.tags overlaps sensitive_docs)
                    and (not to.value in {str matching r".*@trustedcorp\.com"});
            }
        """,
        language="sqrt",
    )
)

fine_grained_config = FineGrainedConfigHeader(
    fsm=FsmOverrides(
        max_n_turns=10,
        disable_rllm=False,
        max_pllm_steps=5,
    ),
    response_format=ResponseFormatOverrides(
        include_program=True,
        include_policy_check_history=True,
    ),
)

# dump_for_headers() serializes each object to a JSON string ready to be
# placed directly in an HTTP header value.
x_features = features.dump_for_headers()
x_policy = security_policy.dump_for_headers()
x_config = fine_grained_config.dump_for_headers()
# --8<-- [end:build_headers]


# --8<-- [start:chat_completion_func]
service_provider = "openrouter"
model = "openai/gpt-5-mini,openai/gpt-5-nano"  # Dual-LLM: PLLM, QLLM


def chat_completion(messages):
    url = f"{base_url}/control/chat/{service_provider}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sequrity_key}",
        "Content-Type": "application/json",
        "X-Api-Key": openrouter_api_key,
        "X-Features": x_features,
        "X-Policy": x_policy,
        "X-Config": x_config,
    }
    payload = {"messages": messages, "model": model}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


# --8<-- [end:chat_completion_func]

if __name__ == "__main__":
    messages = [{"role": "user", "content": "What is the largest prime number below 100?"}]
    result = chat_completion(messages)
    print(result)
