"""Sequrity Control product.

This package provides the client, resources, types, and integrations
for the Sequrity Control API.

Example:
    ```python
    from sequrity import SequrityClient
    from sequrity.control import ControlConfig, FeaturesHeader, SecurityPolicyHeader

    client = SequrityClient(
        api_key="sq-xxx",
        control=ControlConfig(
            features=FeaturesHeader.dual_llm(),
            security_policy=SecurityPolicyHeader.dual_llm(),
        ),
    )

    response = client.control.chat.create(
        messages=[{"role": "user", "content": "Hello!"}],
        model="gpt-5-mini",
    )
    ```
"""

from ._config import ControlConfig
from ._stream import AsyncStream, SyncStream
from .types.dual_llm_response import (
    ErrorInfo,
    MetaData,
    ResponseContentJsonSchema,
    ValueWithMeta,
)
from .types.enums import EndpointType
from .types.headers import (
    ConstraintConfig,
    ControlFlowMetaPolicy,
    FeaturesHeader,
    FineGrainedConfigHeader,
    FsmOverrides,
    InternalPolicyPresets,
    SecurityPolicyHeader,
    TaggerConfig,
)
from .types.policy_gen import PolicyGenRequest, PolicyGenResponse

__all__ = [
    # Config
    "ControlConfig",
    # Enums
    "EndpointType",
    # Headers
    "FeaturesHeader",
    "SecurityPolicyHeader",
    "FineGrainedConfigHeader",
    "FsmOverrides",
    "TaggerConfig",
    "ConstraintConfig",
    "ControlFlowMetaPolicy",
    "InternalPolicyPresets",
    # Dual-LLM response types
    "MetaData",
    "ValueWithMeta",
    "ErrorInfo",
    "ResponseContentJsonSchema",
    # Streaming
    "SyncStream",
    "AsyncStream",
    # Policy generation
    "PolicyGenRequest",
    "PolicyGenResponse",
]
