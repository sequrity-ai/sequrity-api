# --8<-- [start:imports]
import os

from sequrity import SequrityClient
from sequrity.control.types import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader
from sequrity.control.types.headers import FsmOverrides, PolicyCode, ResponseFormatOverrides

# --8<-- [end:imports]

# --8<-- [start:api_keys]
sequrity_key = os.getenv("SEQURITY_API_KEY", "your-sequrity-api-key")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
# --8<-- [end:api_keys]

# --8<-- [start:build_headers]
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
# --8<-- [end:build_headers]

# --8<-- [start:send_request]
client = SequrityClient(api_key=sequrity_key)

response = client.control.chat.create(
    messages=[{"role": "user", "content": "What is the largest prime number below 100?"}],
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    llm_api_key=openrouter_api_key,
    provider="openrouter",
    features=features,
    security_policy=security_policy,
    fine_grained_config=fine_grained_config,
)

print(response)
# --8<-- [end:send_request]
