"""Fine-grained configuration header types for Sequrity Control API.

This module defines advanced configuration options for session behavior,
response formatting, and internal tool settings.
"""

import json
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, ValidationError

OptionalInternalSoToolIdType: TypeAlias = Literal["parse_with_ai", "verify_hypothesis"]
DebugInfoLevel: TypeAlias = Literal["minimal", "normal", "extra"]


class ResponseFormat(BaseModel):
    strip_response_content: bool = Field(
        default=False, description="Whether to strip the response content. This overrides other inclusion settings."
    )
    include_program: bool = Field(default=False, description="Whether to include the final program in the response.")
    include_policy_check_history: bool = Field(
        default=False, description="Whether to include the policy check history in the response."
    )
    include_namespace_snapshot: bool = Field(
        default=False, description="Whether to include the namespace screenshot in the response."
    )

    model_config = ConfigDict(extra="forbid")


class FineGrainedConfigHeader(BaseModel):
    """
    Schema for session configuration from HTTP headers.

    Note: The default values here do not matter since we use exclude_unset when converting to SessionConfig.
    """

    max_pllm_attempts: int = Field(
        default=4, description="Maximum number of PLLM attempts before giving up and returning an error.", ge=1
    )
    merge_system_messages: bool = Field(
        default=True, description="Whether to merge multiple system messages into one before sending to PLLM."
    )
    convert_system_to_developer_messages: bool = Field(
        default=False, description="Whether to convert system messages to developer messages in the user query."
    )
    include_other_roles_in_user_query: list[Literal["assistant", "tool"]] = Field(
        default=["assistant"],
        description="List of roles to include in the user query besides 'user'.",
    )
    max_tool_calls_per_attempt: int | None = Field(
        default=200,
        description="Maximum number of tool calls allowed per PLLM attempt. If None, no limit is enforced.",
        ge=1,
    )
    clear_history_every_n_attempts: int | None = Field(
        default=None,
        description="If set, the session will clear the tool call history every n PLLM attempts to save token usage.",
        ge=1,
    )
    retry_on_policy_violation: bool = Field(
        default=False,
        description="If True, the session will retry PLLM attempts when a policy violation is detected.",
    )
    cache_tool_result: Literal["none", "all", "deterministic-only"] = Field(
        default="deterministic-only",
        description="Cache tool results to avoid redundant calls. 'none': no caching; 'all': cache all tool results; 'deterministic': cache only deterministic tool results.",
    )
    force_to_cache: list[str] = Field(
        default_factory=list,
        description="List of tool ID regex patterns to always cache their results regardless of the cache_tool_result setting.",
    )
    # tool filtering
    min_num_tools_for_filtering: int | None = Field(
        default=10,
        description="Minimum number of available tools to trigger tool filtering. If the number of available tools is less than this, no filtering is performed.",
        ge=2,
    )
    clear_session_meta: Literal["never", "every_attempt", "every_turn"] = Field(
        default="never",
        description="When to clear session meta information. 'never': never clear; 'every_attempt': clear at the beginning of each PLLM attempt; 'every_turn': clear at the beginning of each turn.",
    )
    disable_rllm: bool = Field(
        default=False, description="If True, disable the Response LLM (RLLM) for reviewing final responses."
    )
    reduced_grammar_for_rllm_review: bool = Field(
        default=True, description="Whether to use a reduced grammar for the RLLM review process."
    )
    rllm_confidence_score_threshold: float | None = Field(
        default=None, ge=0.0, le=1.0, description="The threshold for accepting RLLM review confidence scores."
    )
    pllm_debug_info_level: DebugInfoLevel = Field(
        default="normal", description="The detail level of debug information provided to the PLLM."
    )
    max_n_turns: int | None = Field(
        default=1,
        ge=1,
        description="Maximum number of turns allowed in the session. If None, unlimited turns are allowed.",
    )
    enable_multi_step_planning: bool = Field(
        default=False, description="If True, enable multi-step planning for complex user queries."
    )
    prune_failed_steps: bool = Field(
        default=True, description="If True, prune failed PLLM steps from session history to save tokens."
    )
    enabled_internal_tools: list[OptionalInternalSoToolIdType] = Field(
        default=["parse_with_ai", "verify_hypothesis"],
    )
    restate_user_query_before_planning: bool = Field(
        default=False,
        description="If True, the user query will be restated before planning to provide clearer context.",
    )
    pllm_can_ask_for_clarification: bool = Field(
        default=False,
        description="If True, allow the PLLM to ask clarifying questions when the user query is ambiguous.",
    )
    reduced_grammar_version: Literal["v1", "v2"] = Field(
        default="v2", description="Version of the reduced grammar to use for RLLM review."
    )

    # response format
    response_format: ResponseFormat = Field(
        default_factory=lambda: ResponseFormat(),
        description="Configuration for the response format.",
    )
    show_pllm_secure_var_values: Literal["none", "basic-notext", "basic-executable", "all-executable"] = Field(
        default="none",
        description="""Whether to show secure variable values to the PLLM in the prompts.
- 'none': do not show any secure variable values
- 'basic-notext': show values of basic types (bool, int, float, list, tuple)
- 'basic-executable': show values of basic types and marked as executable memory variables
- 'all-executable': show all variables marked as executable memory

"basic-executable" and "all-executable" require enable_non_executable_memory to be True in internal policy preset.
""",
    )

    model_config = ConfigDict(extra="forbid")

    def dump_for_headers(self, mode: Literal["json", "json_str"] = "json_str") -> dict | str:
        if mode == "json":
            return self.model_dump(mode="json", exclude_unset=True)
        elif mode == "json_str":
            return self.model_dump_json(exclude_unset=True)
        else:
            raise ValueError(f"Unsupported mode for dump_for_headers: {mode}")
