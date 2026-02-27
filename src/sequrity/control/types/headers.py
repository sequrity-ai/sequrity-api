"""Sequrity Control API header types.

This module defines the configuration classes for the three Sequrity
HTTP headers: ``X-Features``, ``X-Policy``, and ``X-Config``.
"""

from __future__ import annotations

import json
from typing import Any, Literal, TypeAlias, overload

from pydantic import BaseModel, ConfigDict, Field


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge *overrides* into *base* (mutates *base*). Override values win."""
    for key, value in overrides.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


# ---------------------------------------------------------------------------
# X-Features header  (FeaturesHeader)
# ---------------------------------------------------------------------------

AgentArch: TypeAlias = Literal["single-llm", "dual-llm"]
ContentClassifierName: TypeAlias = Literal[
    "pii_redaction", "toxicity_filter", "healthcare_topic_guardrail", "finance_topic_guardrail"
]
ContentBlockerName: TypeAlias = Literal["url_blocker", "file_blocker"]


class TaggerConfig(BaseModel):
    """Configuration for a content classifier.

    Attributes:
        name: Classifier identifier.
        threshold: Detection sensitivity threshold (0.0-1.0).
        mode: Optional mode that overrides threshold (e.g., "high sensitivity", "strict", "low sensitivity", "normal").
    """

    model_config = ConfigDict(extra="forbid")

    name: ContentClassifierName = Field(description="Classifier identifier.")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Threshold for the tagger.")
    mode: str | None = Field(
        default=None,
        description="Optional mode that overrides threshold (e.g., 'high sensitivity', 'strict', 'low sensitivity', 'normal').",
    )


class ConstraintConfig(BaseModel):
    """Configuration for a content blocker.

    Attributes:
        name: Blocker identifier ("url_blocker" or "file_blocker").
    """

    model_config = ConfigDict(extra="forbid")

    name: ContentBlockerName = Field(description="Blocker identifier ('url_blocker' or 'file_blocker').")


class FeaturesHeader(BaseModel):
    """Configuration header for Sequrity security features (``X-Features``).

    Sent as a JSON object with agent architecture selection and optional
    content classifiers/blockers.

    Example:
        ```python
        features = FeaturesHeader.single_llm(toxicity_filter=True)
        features = FeaturesHeader.dual_llm(pii_redaction=True, url_blocker=True)
        ```
    """

    model_config = ConfigDict(extra="forbid")

    agent_arch: AgentArch | None = Field(None, description="Agent architecture: single-llm or dual-llm.")
    content_classifiers: list[TaggerConfig] | None = Field(
        None,
        description="LLM-based content classifiers that analyze tool call arguments (pre-execution) and results (post-execution) to detect sensitive content (e.g., PII, toxicity).",
    )
    content_blockers: list[ConstraintConfig] | None = Field(
        None,
        description="Content blockers that redact or mask sensitive content in tool call arguments (pre-execution) and results (post-execution).",
    )

    @overload
    def dump_for_headers(self, mode: Literal["json_str"] = ..., *, overrides: dict[str, Any] | None = ...) -> str: ...
    @overload
    def dump_for_headers(self, mode: Literal["json"], *, overrides: dict[str, Any] | None = ...) -> dict: ...

    def dump_for_headers(
        self, mode: Literal["json", "json_str"] = "json_str", *, overrides: dict[str, Any] | None = None
    ) -> dict | str:
        """Serialize for use as the ``X-Features`` HTTP header value.

        Args:
            mode: Output format — ``"json"`` for a dict, ``"json_str"`` for a JSON string.
            overrides: Optional dict to deep-merge into the serialized output.
                Allows adding or overriding fields not defined on the model
                without loosening Pydantic validation.
        """
        data = self.model_dump(mode="json", exclude_none=True)
        if overrides:
            _deep_merge(data, overrides)
        if mode == "json":
            return data
        elif mode == "json_str":
            return json.dumps(data)
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'json' or 'json_str'.")

    @classmethod
    def _build(
        cls,
        arch: AgentArch,
        toxicity_filter: bool,
        pii_redaction: bool,
        healthcare_guardrail: bool,
        finance_guardrail: bool,
        url_blocker: bool,
        file_blocker: bool,
    ) -> FeaturesHeader:
        classifiers: list[TaggerConfig] = []
        if toxicity_filter:
            classifiers.append(TaggerConfig(name="toxicity_filter"))
        if pii_redaction:
            classifiers.append(TaggerConfig(name="pii_redaction"))
        if healthcare_guardrail:
            classifiers.append(TaggerConfig(name="healthcare_topic_guardrail"))
        if finance_guardrail:
            classifiers.append(TaggerConfig(name="finance_topic_guardrail"))

        blockers: list[ConstraintConfig] = []
        if url_blocker:
            blockers.append(ConstraintConfig(name="url_blocker"))
        if file_blocker:
            blockers.append(ConstraintConfig(name="file_blocker"))

        return cls(
            agent_arch=arch,
            content_classifiers=classifiers if classifiers else None,
            content_blockers=blockers if blockers else None,
        )

    @classmethod
    def single_llm(
        cls,
        toxicity_filter: bool = False,
        pii_redaction: bool = False,
        healthcare_guardrail: bool = False,
        finance_guardrail: bool = False,
        url_blocker: bool = False,
        file_blocker: bool = False,
    ) -> FeaturesHeader:
        """Create a Single LLM features configuration."""
        return cls._build(
            "single-llm",
            toxicity_filter,
            pii_redaction,
            healthcare_guardrail,
            finance_guardrail,
            url_blocker,
            file_blocker,
        )

    @classmethod
    def dual_llm(
        cls,
        toxicity_filter: bool = False,
        pii_redaction: bool = False,
        healthcare_guardrail: bool = False,
        finance_guardrail: bool = False,
        url_blocker: bool = False,
        file_blocker: bool = False,
    ) -> FeaturesHeader:
        """Create a Dual LLM features configuration."""
        return cls._build(
            "dual-llm",
            toxicity_filter,
            pii_redaction,
            healthcare_guardrail,
            finance_guardrail,
            url_blocker,
            file_blocker,
        )


# ---------------------------------------------------------------------------
# X-Policy header  (SecurityPolicyHeader)
# ---------------------------------------------------------------------------


class ControlFlowMetaPolicy(BaseModel):
    """Control flow meta policy for branching tools."""

    mode: Literal["allow", "deny"] = Field(default="deny", description="'allow' for whitelist, 'deny' for blacklist.")
    producers: set[str] = Field(
        default_factory=set, description="Set of prohibited producers for control flow relaxer in custom mode."
    )
    tags: set[str] = Field(
        default_factory=set, description="Set of prohibited tags for control flow relaxer in custom mode."
    )
    consumers: set[str] = Field(
        default_factory=set, description="Set of prohibited consumers for control flow relaxer in custom mode."
    )


class InternalPolicyPresets(BaseModel):
    """Internal policy presets for advanced policy configuration."""

    model_config = ConfigDict(extra="forbid")

    default_allow: bool = Field(default=True, description="Whether to allow tool calls by default.")
    default_allow_enforcement_level: Literal["hard", "soft"] = Field(
        default="soft", description="Enforcement level for default allow policy."
    )
    enable_non_executable_memory: bool = Field(
        default=True,
        description="Whether to enable non-executable memory internal policy (attach non-executable tag to all tool results by default).",
    )
    branching_meta_policy: ControlFlowMetaPolicy = Field(
        default_factory=ControlFlowMetaPolicy,
        description="Control flow meta policy for branching tools.",
    )
    enable_llm_blocked_tag: bool = Field(
        default=True,
        description="Whether to enable LLM blocked tag internal policy (denies tool calls to parse_with_ai if any argument has LLM_BLOCKED_TAG).",
    )
    llm_blocked_tag_enforcement_level: Literal["hard", "soft"] = Field(
        default="hard", description="Enforcement level for LLM blocked tag internal policy."
    )


class PolicyCode(BaseModel):
    """Security policy code container.

    Attributes:
        code: The security policy code as a single string.
        language: The language of the policy code ("sqrt" or "cedar").
    """

    model_config = ConfigDict(extra="forbid")

    code: str = Field(default="", description="The security policy code as a single string.")
    language: Literal["sqrt", "cedar"] = Field(default="sqrt", description="The language of the policy code.")


class SecurityPolicyHeader(BaseModel):
    """Configuration header for Sequrity security policies (``X-Policy``).

    Defines the rules and constraints that govern LLM behavior.

    Example:
        ```python
        policy = SecurityPolicyHeader.dual_llm(codes="allow tool x;")
        policy = SecurityPolicyHeader.single_llm()
        ```
    """

    model_config = ConfigDict(extra="forbid")

    mode: Literal["standard", "strict", "custom"] | None = Field(
        default=None, description="The security mode: standard, strict, or custom."
    )
    codes: PolicyCode | None = Field(default=None, description="User security policy code.")
    auto_gen: bool | None = Field(
        default=None,
        description="Whether to auto-generate policies based on tool metadata and natural language descriptions.",
    )
    fail_fast: bool | None = Field(
        default=None, description="Whether to fail fast on first hard denial during policy checks."
    )
    presets: InternalPolicyPresets | None = Field(default=None, description="Internal policy presets configuration.")

    @overload
    def dump_for_headers(self, mode: Literal["json_str"] = ..., *, overrides: dict[str, Any] | None = ...) -> str: ...
    @overload
    def dump_for_headers(self, mode: Literal["json"], *, overrides: dict[str, Any] | None = ...) -> dict: ...

    def dump_for_headers(
        self, mode: Literal["json", "json_str"] = "json_str", *, overrides: dict[str, Any] | None = None
    ) -> dict | str:
        """Serialize for use as the ``X-Policy`` HTTP header value.

        Args:
            mode: Output format — ``"json"`` for a dict, ``"json_str"`` for a JSON string.
            overrides: Optional dict to deep-merge into the serialized output.
        """
        data = self.model_dump(mode="json", exclude_none=True)
        if overrides:
            _deep_merge(data, overrides)
        if mode == "json":
            return data
        elif mode == "json_str":
            return json.dumps(data)
        else:
            raise ValueError(f"Unsupported mode for dump_for_headers: {mode}")

    @classmethod
    def dual_llm(
        cls,
        mode: Literal["standard", "strict", "custom"] = "standard",
        codes: str = "",
        language: Literal["sqrt", "cedar"] = "sqrt",
        auto_gen: bool = False,
        fail_fast: bool | None = None,
        default_allow: bool = True,
        default_allow_enforcement_level: Literal["hard", "soft"] = "soft",
        enable_non_executable_memory: bool = True,
        enable_llm_blocked_tag: bool = True,
        llm_blocked_tag_enforcement_level: Literal["hard", "soft"] = "hard",
        branching_meta_policy_mode: Literal["allow", "deny"] = "deny",
        branching_meta_policy_producers: set[str] | None = None,
        branching_meta_policy_tags: set[str] | None = None,
        branching_meta_policy_consumers: set[str] | None = None,
    ) -> SecurityPolicyHeader:
        """Create a Dual LLM security policy configuration."""
        return cls.model_validate(
            {
                "mode": mode,
                "codes": {"code": codes, "language": language},
                "auto_gen": auto_gen,
                "fail_fast": fail_fast,
                "presets": {
                    "default_allow": default_allow,
                    "default_allow_enforcement_level": default_allow_enforcement_level,
                    "enable_non_executable_memory": enable_non_executable_memory,
                    "enable_llm_blocked_tag": enable_llm_blocked_tag,
                    "llm_blocked_tag_enforcement_level": llm_blocked_tag_enforcement_level,
                    "branching_meta_policy": {
                        "mode": branching_meta_policy_mode,
                        "producers": branching_meta_policy_producers or set(),
                        "tags": branching_meta_policy_tags or set(),
                        "consumers": branching_meta_policy_consumers or set(),
                    },
                },
            }
        )

    @classmethod
    def single_llm(
        cls,
        mode: Literal["standard", "strict", "custom"] = "standard",
        codes: str = "",
        language: Literal["sqrt", "cedar"] = "sqrt",
        fail_fast: bool | None = None,
        default_allow: bool = True,
        enable_llm_blocked_tag: bool = True,
        llm_blocked_tag_enforcement_level: Literal["hard", "soft"] = "hard",
    ) -> SecurityPolicyHeader:
        """Create a Single LLM security policy configuration."""
        return cls.model_validate(
            {
                "mode": mode,
                "codes": {"code": codes, "language": language},
                "auto_gen": False,
                "fail_fast": fail_fast,
                "presets": {
                    "default_allow": default_allow,
                    "enable_non_executable_memory": False,
                    "enable_llm_blocked_tag": enable_llm_blocked_tag,
                    "llm_blocked_tag_enforcement_level": llm_blocked_tag_enforcement_level,
                },
            }
        )


# ---------------------------------------------------------------------------
# X-Config header  (FineGrainedConfigHeader)
# ---------------------------------------------------------------------------

InternalSqrtToolIdType: TypeAlias = Literal["parse_with_ai", "verify_hypothesis", "set_policy", "complete_turn"]
DebugInfoLevel: TypeAlias = Literal["minimal", "normal", "extra"]
PromptFlavor: TypeAlias = str
PromptVersion: TypeAlias = str
MessageRoleType: TypeAlias = str


class FsmOverrides(BaseModel):
    """Overrideable FSM fields (shared + dual-llm-only).

    Single-LLM configs silently ignore dual-llm-only fields.
    """

    model_config = ConfigDict(extra="forbid")

    # Shared (single-llm & dual-llm)
    min_num_tools_for_filtering: int | None = Field(
        default=None,
        description="Minimum number of registered tools to enable tool-filtering LLM step. Set to None to disable.",
    )
    clear_session_meta: Literal["never", "every_attempt", "every_turn"] | None = Field(
        default=None,
        description="When to clear session meta information. 'never': never clear; 'every_attempt': clear at the beginning of each PLLM attempt; 'every_turn': clear at the beginning of each turn.",
    )
    max_n_turns: int | None = Field(
        default=None,
        description="Maximum number of turns allowed in the session. If None, unlimited turns are allowed.",
    )

    # Dual-LLM only
    history_mismatch_policy: Literal["reject", "restart_turn", "continue"] | None = Field(
        default=None,
        description="Controls behaviour when incoming messages diverge from stored history in stateless mode. 'reject' rejects the request with an error, 'restart_turn' truncates stored history to the last consistent point and restarts the turn, 'continue' silently accepts the caller's version and continues.",
    )
    clear_history_every_n_attempts: int | None = Field(
        default=None,
        description="Single-step mode only. Clear all failed step history every N attempts to save tokens.",
    )
    disable_rllm: bool | None = Field(default=None, description="Whether to skip the response LLM (RLLM) review step.")
    enable_multistep_planning: bool | None = Field(
        default=None,
        description="When False (single-step), each attempt solves independently. When True (multi-step), each step builds on previous.",
    )
    enabled_internal_tools: list[InternalSqrtToolIdType] | None = Field(
        default=None, description="List of internal tool IDs available to planning LLM."
    )
    prune_failed_steps: bool | None = Field(
        default=None, description="Multi-step mode only. Remove failed steps from history after turn completes."
    )
    force_to_cache: list[str] | None = Field(
        default=None,
        description="List of tool ID regex patterns to always cache their results regardless of the cache_tool_result setting.",
    )
    max_pllm_steps: int | None = Field(default=None, description="Maximum number of steps allowed per turn.")
    max_pllm_failed_steps: int | None = Field(
        default=None, description="Maximum number of failed steps allowed per turn."
    )
    max_tool_calls_per_step: int | None = Field(
        default=None,
        description="Maximum number of tool calls allowed per PLLM attempt. If None, no limit is enforced.",
    )
    reduced_grammar_for_rllm_review: bool | None = Field(
        default=None,
        description="Whether to paraphrase RLLM output via reduced grammar before feeding back to planning LLM.",
    )
    retry_on_policy_violation: bool | None = Field(
        default=None,
        description="When True, allow planning LLM to retry after policy violation.",
    )
    wrap_tool_result: bool | None = Field(
        default=None,
        description="Whether to wrap tool results in Ok/Err types.",
    )
    detect_tool_errors: Literal["none", "regex", "llm"] | None = Field(
        default=None,
        description="Whether and how to detect errors in tool results. 'none': do not detect; 'regex': use regex patterns; 'llm': use an LLM to analyze tool results.",
    )
    detect_tool_error_regex_pattern: str | None = Field(
        default=None,
        description="The regex pattern to use for detecting error messages in tool results when detect_tool_errors is set to 'regex'.",
    )
    detect_tool_error_max_result_length: int | None = Field(
        default=None,
        description="The maximum length of tool result to consider for error detection. Longer results will be truncated. If None, no limit is enforced.",
    )
    strict_tool_result_parsing: bool | None = Field(
        default=None,
        description="If True, only parse external tool results as JSON when the tool declares an output_schema. When False, always attempt json.loads on tool results.",
    )
    tool_result_transform: Literal["none", "codex"] | None = Field(
        default=None,
        description="Transform applied to tool result values before error detection. "
        "'none': no transform; 'codex': strip Codex CLI metadata prefix and "
        "extract exit code + output.",
    )


class PllmPromptOverrides(BaseModel):
    """Overrideable PLLM prompt fields."""

    model_config = ConfigDict(extra="forbid")

    flavor: PromptFlavor | str | None = Field(
        default=None, description="Prompt template variant to use (e.g., 'universal')."
    )
    version: PromptVersion | str | None = Field(
        default=None,
        description="Prompt template version. Combined with flavor to load template.",
    )
    clarify_ambiguous_queries: bool | None = Field(
        default=None, description="Whether planning LLM is allowed to ask for clarification on ambiguous queries."
    )
    context_var_visibility: Literal["none", "basic-notext", "basic-executable", "all-executable", "all"] | None = Field(
        default=None,
        description="The visibility level of context variables in the PLLM prompts. 'none': do not show any; 'basic-notext': show basic types but not text; 'basic-executable': show basic types and executable memory variables; 'all-executable': show all executable memory variables; 'all': show all.",
    )
    query_inline_roles: list[Literal["assistant", "tool", "developer", "system"]] | None = Field(
        default=None, description="List of roles whose messages will be inlined into the user query."
    )
    query_role_name_overrides: dict[MessageRoleType, MessageRoleType] | None = Field(
        default=None,
        description="Overrides for message role names in the inlined user query. For example, {'assistant': 'developer'} will change the role of assistant messages to developer.",
    )
    query_include_tool_calls: bool | None = Field(
        default=None,
        description="Whether to include upstream tool calls in inlined query.",
    )
    query_include_tool_args: bool | None = Field(
        default=None,
        description="Whether to include arguments of upstream tool calls.",
    )
    query_include_tool_results: bool | None = Field(
        default=None,
        description="Whether to include results of upstream tool calls.",
    )
    debug_info_level: DebugInfoLevel | None = Field(
        default=None, description="Level of detail for debug/execution information in planning LLM prompt."
    )


class RllmPromptOverrides(BaseModel):
    """Overrideable RLLM prompt fields."""

    model_config = ConfigDict(extra="forbid")

    flavor: PromptFlavor | str | None = Field(
        default=None, description="Prompt template variant to use (e.g., 'universal')."
    )
    version: PromptVersion | str | None = Field(
        default=None,
        description="Prompt template version. Combined with flavor to load template.",
    )
    debug_info_level: DebugInfoLevel | None = Field(
        default=None, description="Level of detail for debug/execution information in RLLM prompt."
    )


class TllmPromptOverrides(BaseModel):
    """Overrideable TLLM (tool-formulating LLM) prompt fields."""

    model_config = ConfigDict(extra="forbid")

    flavor: PromptFlavor | str | None = Field(
        default=None, description="Prompt template variant to use (e.g., 'universal')."
    )
    version: PromptVersion | str | None = Field(
        default=None,
        description="Prompt template version. Combined with flavor to load template.",
    )
    add_tool_description: bool | None = Field(
        default=None, description="Whether to include tool descriptions in tool-filtering prompt."
    )
    add_tool_input_schema: bool | None = Field(
        default=None, description="Whether to include tool input JSON schemas in tool-filtering prompt."
    )


class LlmPromptOverrides(BaseModel):
    """Base overrides for other LLM types (GRLLM, QLLM, etc.)."""

    model_config = ConfigDict(extra="forbid")

    flavor: PromptFlavor | str | None = Field(
        default=None, description="Prompt template variant to use (e.g., 'universal')."
    )
    version: PromptVersion | str | None = Field(
        default=None,
        description="Prompt template version. Combined with flavor to load template.",
    )


class PromptOverrides(BaseModel):
    """Prompt overrides for all LLMs."""

    model_config = ConfigDict(extra="forbid")

    pllm: PllmPromptOverrides | None = Field(default=None, description="Configuration for the planning LLM prompt.")
    rllm: RllmPromptOverrides | None = Field(default=None, description="Configuration for the review LLM prompt.")
    grllm: LlmPromptOverrides | None = Field(default=None, description="Configuration for the GRLLM prompt.")
    qllm: LlmPromptOverrides | None = Field(default=None, description="Configuration for the QLLM prompt.")
    tllm: TllmPromptOverrides | None = Field(
        default=None, description="Configuration for the tool-formulating LLM prompt."
    )
    tagllm: LlmPromptOverrides | None = Field(default=None, description="Configuration for the tag LLM prompt.")
    policy_llm: LlmPromptOverrides | None = Field(default=None, description="Configuration for the policy LLM prompt.")
    error_detector_llm: LlmPromptOverrides | None = Field(
        default=None, description="Configuration for the error detector LLM prompt."
    )


class ResponseFormatOverrides(BaseModel):
    """Overrideable response-format fields (dual-llm only)."""

    model_config = ConfigDict(extra="forbid")

    strip_response_content: bool | None = Field(
        default=None,
        description="When True, returns only essential result value as plain text, stripping all metadata.",
    )
    include_program: bool | None = Field(
        default=None, description="Whether to include the generated program in the response."
    )
    include_policy_check_history: bool | None = Field(
        default=None, description="Whether to include policy check results even when there are no violations."
    )
    include_namespace_snapshot: bool | None = Field(
        default=None, description="Whether to include snapshot of all variables after program execution."
    )


class FineGrainedConfigHeader(BaseModel):
    """Structured configuration header (``X-Config``).

    Groups overrides into FSM, prompt, and response format sections.

    Example:
        ```python
        config = FineGrainedConfigHeader.dual_llm(
            max_n_turns=10,
            disable_rllm=False,
            include_program=True,
        )
        config = FineGrainedConfigHeader.single_llm(max_n_turns=50)
        ```
    """

    model_config = ConfigDict(extra="forbid")

    fsm: FsmOverrides | None = Field(default=None, description="FSM configuration overrides.")
    prompt: PromptOverrides | None = Field(default=None, description="Prompt configuration overrides for all LLMs.")
    response_format: ResponseFormatOverrides | None = Field(
        default=None, description="Response format configuration for dual-LLM sessions."
    )

    @overload
    def dump_for_headers(self, mode: Literal["json_str"] = ..., *, overrides: dict[str, Any] | None = ...) -> str: ...
    @overload
    def dump_for_headers(self, mode: Literal["json"], *, overrides: dict[str, Any] | None = ...) -> dict: ...

    def dump_for_headers(
        self, mode: Literal["json", "json_str"] = "json_str", *, overrides: dict[str, Any] | None = None
    ) -> dict | str:
        """Serialize for use as the ``X-Config`` HTTP header value.

        Args:
            mode: Output format — ``"json"`` for a dict, ``"json_str"`` for a JSON string.
            overrides: Optional dict to deep-merge into the serialized output.
                Nested dicts are merged recursively; non-dict values replace
                existing ones. This lets you inject fields the Pydantic model
                doesn't define while keeping ``extra="forbid"`` validation at
                construction time.

        Example:
            ```python
            config = FineGrainedConfigHeader.dual_llm(max_n_turns=5)
            header_json = config.dump_for_headers(overrides={
                "fsm": {
                    "max_n_turns": 20,              # override existing
                    "custom_beta_flag": True,       # add custom field that is not defined on the model
                },
                "prompt": {
                    "pllm": {"debug_info_level": "extra"},  # nested override
                },
                "experimental_section": {"key": "value"},   # new top-level key
            })
            ```
        """
        data = self.model_dump(mode="json", exclude_none=True)
        if overrides:
            _deep_merge(data, overrides)
        if mode == "json":
            return data
        elif mode == "json_str":
            return json.dumps(data)
        else:
            raise ValueError(f"Unsupported mode for dump_for_headers: {mode}")

    @classmethod
    def single_llm(
        cls,
        min_num_tools_for_filtering: int | None = 10,
        clear_session_meta: Literal["never", "every_attempt", "every_turn"] = "never",
        max_n_turns: int | None = 50,
    ) -> FineGrainedConfigHeader:
        """Create a Single LLM fine-grained configuration."""
        return cls(
            fsm=FsmOverrides(
                min_num_tools_for_filtering=min_num_tools_for_filtering,
                clear_session_meta=clear_session_meta,
                max_n_turns=max_n_turns,
            ),
        )

    @classmethod
    def dual_llm(
        cls,
        # FSM shared
        min_num_tools_for_filtering: int | None = 10,
        clear_session_meta: Literal["never", "every_attempt", "every_turn"] = "never",
        max_n_turns: int | None = 5,
        # FSM dual-llm only
        clear_history_every_n_attempts: int | None = None,
        disable_rllm: bool | None = True,
        enable_multistep_planning: bool | None = None,
        enabled_internal_tools: list[InternalSqrtToolIdType] | None = None,
        prune_failed_steps: bool | None = None,
        force_to_cache: list[str] | None = None,
        max_pllm_steps: int | None = None,
        max_pllm_failed_steps: int | None = None,
        max_tool_calls_per_step: int | None = None,
        reduced_grammar_for_rllm_review: bool | None = None,
        retry_on_policy_violation: bool | None = None,
        # Prompt
        pllm_debug_info_level: DebugInfoLevel | None = None,
        # Response format
        strip_response_content: bool | None = None,
        include_program: bool | None = None,
        include_policy_check_history: bool | None = None,
        include_namespace_snapshot: bool | None = None,
    ) -> FineGrainedConfigHeader:
        """Create a Dual LLM fine-grained configuration."""
        fsm = FsmOverrides(
            min_num_tools_for_filtering=min_num_tools_for_filtering,
            clear_session_meta=clear_session_meta,
            max_n_turns=max_n_turns,
            clear_history_every_n_attempts=clear_history_every_n_attempts,
            disable_rllm=disable_rllm,
            enable_multistep_planning=enable_multistep_planning,
            enabled_internal_tools=enabled_internal_tools,
            prune_failed_steps=prune_failed_steps,
            force_to_cache=force_to_cache,
            max_pllm_steps=max_pllm_steps,
            max_pllm_failed_steps=max_pllm_failed_steps,
            max_tool_calls_per_step=max_tool_calls_per_step,
            reduced_grammar_for_rllm_review=reduced_grammar_for_rllm_review,
            retry_on_policy_violation=retry_on_policy_violation,
        )

        prompt = None
        if pllm_debug_info_level is not None:
            prompt = PromptOverrides(
                pllm=PllmPromptOverrides(debug_info_level=pllm_debug_info_level),
            )

        response_fmt = None
        if any(
            v is not None
            for v in [strip_response_content, include_program, include_policy_check_history, include_namespace_snapshot]
        ):
            response_fmt = ResponseFormatOverrides(
                strip_response_content=strip_response_content,
                include_program=include_program,
                include_policy_check_history=include_policy_check_history,
                include_namespace_snapshot=include_namespace_snapshot,
            )

        return cls(
            fsm=fsm,
            prompt=prompt,
            response_format=response_fmt,
        )
