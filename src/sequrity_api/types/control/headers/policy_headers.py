"""Security policy header types for Sequrity Control API.

This module defines the configuration classes for security policies
including policy language, codes, and internal policy presets.
"""

import json
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, ValidationError

OptionalInternalSoToolIdType: TypeAlias = Literal["parse_with_ai", "verify_hypothesis"]
DebugInfoLevel: TypeAlias = Literal["minimal", "normal", "extra"]


# Tag for non-executable memory data
NON_EXECUTABLE_MEM_TAG = "__non_executable"

# Tag for parse_with_ai tool results
PARSE_WITH_AI_TAG = "__tool/parse_with_ai"


class ControlFlowMetaPolicy(BaseModel):
    mode: Literal["allow", "deny"] = Field(default="deny", description="'allow' for whitelist, 'deny' for blacklist.")
    producers: tuple[str, ...] = Field(
        default_factory=tuple, description="Set of prohibited producers for control flow relaxer in custom mode."
    )
    tags: tuple[str, ...] = Field(
        default_factory=tuple, description="Set of prohibited tags for control flow relaxer in custom mode."
    )
    consumers: tuple[str, ...] = Field(
        default_factory=tuple, description="Set of prohibited consumers for control flow relaxer in custom mode."
    )


class InternalPolicyPreset(BaseModel):
    default_allow: bool = Field(default=True, description="Whether to allow tool calls by default.")
    enable_non_executable_memory: bool = Field(
        default=True, description="Inject non-executable to tool result tags by default."
    )
    branching_meta_policy: ControlFlowMetaPolicy = Field(
        default_factory=lambda: ControlFlowMetaPolicy(mode="deny"),
        description="Metadata that are allowed or forbidden in branching.",
    )
    qllm_input_meta_policy: ControlFlowMetaPolicy = Field(
        default_factory=lambda: ControlFlowMetaPolicy(mode="deny"),
        description="Metadata that are allowed or forbidden in QLLM inputs.",
    )


class SecurityPolicyHeader(BaseModel):
    """Configuration header for Sequrity security policies.

    Security policies define the rules and constraints that govern LLM behavior.
    Sequrity supports multiple policy languages: sqrt, sqrt-lite, and cedar.

    Attributes:
        language: The policy language to use ("sqrt", "sqrt-lite", or "cedar").
        codes: The security policy code(s) defining the rules.
        auto_gen: Enable auto-generation mode for relaxed constraints.
        fail_fast: Whether to fail immediately on policy violations.
        internal_policy_preset: Advanced internal policy configuration.

    Example:
        ```python
        # Create a default security policy
        policy = SecurityPolicyHeader.create_default(
            language="sqrt-lite",
            default_allow=True,
        )
        ```
    """

    language: Literal["sqrt", "sqrt-lite", "cedar"] = Field(
        default="sqrt-lite", description="The security policy language to use."
    )
    codes: list[str] | str = Field(default="", description="The security policy codes.")
    auto_gen: bool = Field(
        default=False,
        description="If True, enable auto-generation mode which relaxes certain policy constraints.",
    )
    fail_fast: bool | None = Field(
        default=None,
        description="Whether to fail fast on policy violations. Only applicable for 'sqrt' and 'sqrt-lite' languages.",
    )
    internal_policy_preset: InternalPolicyPreset | None = Field(
        default=None,
        description="The internal policy preset configuration.",
    )

    model_config = ConfigDict(extra="forbid")

    def dump_for_headers(self, mode: Literal["json", "json_str"] = "json_str") -> dict | str:
        if mode == "json":
            return self.model_dump(mode="json", exclude_none=True)
        elif mode == "json_str":
            return self.model_dump_json(exclude_none=True)
        else:
            raise ValueError(f"Unsupported mode for dump_for_headers: {mode}")

    @classmethod
    def create_default(
        cls,
        language: Literal["sqrt", "sqrt-lite", "cedar"] = "sqrt-lite",
        codes: list[str] | str = "",
        auto_gen: bool = False,
        fail_fast: bool | None = None,
        default_allow: bool = True,
        enable_non_executable_memory: bool = True,
        branching_meta_policy_mode: Literal["allow", "deny"] = "deny",
        branching_meta_policy_producers: tuple[str, ...] | None = None,
        branching_meta_policy_tags: tuple[str, ...] | None = None,
        branching_meta_policy_consumers: tuple[str, ...] | None = None,
        qllm_input_meta_policy_mode: Literal["allow", "deny"] = "deny",
        qllm_input_meta_policy_producers: tuple[str, ...] | None = None,
        qllm_input_meta_policy_tags: tuple[str, ...] | None = None,
        qllm_input_meta_policy_consumers: tuple[str, ...] | None = None,
    ) -> "SecurityPolicyHeader":
        obj = cls.model_validate(
            {
                "language": language,
                "codes": codes,
                "auto_gen": auto_gen,
                "fail_fast": fail_fast,
                "internal_policy_preset": {
                    "default_allow": default_allow,
                    "enable_non_executable_memory": enable_non_executable_memory,
                    "branching_meta_policy": {
                        "mode": branching_meta_policy_mode,
                        "producers": branching_meta_policy_producers or (),
                        "tags": branching_meta_policy_tags or (),
                        "consumers": branching_meta_policy_consumers or (),
                    },
                    "qllm_input_meta_policy": {
                        "mode": qllm_input_meta_policy_mode,
                        "producers": qllm_input_meta_policy_producers or (),
                        "tags": qllm_input_meta_policy_tags or (),
                        "consumers": qllm_input_meta_policy_consumers or (),
                    },
                },
            }
        )
        return obj
