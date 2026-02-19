"""Sequrity Control API header types.

This module defines the configuration classes for the three Sequrity
HTTP headers: ``X-Features``, ``X-Policy``, and ``X-Config``.
"""

from typing import Literal, TypeAlias, overload

from pydantic import BaseModel, ConfigDict, Field

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
        mode: Optional mode that overrides threshold ("normal"/"strict").
    """

    model_config = ConfigDict(extra="forbid")

    name: ContentClassifierName
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    mode: str | None = Field(default=None)


class ConstraintConfig(BaseModel):
    """Configuration for a content blocker.

    Attributes:
        name: Blocker identifier ("url_blocker" or "file_blocker").
    """

    model_config = ConfigDict(extra="forbid")

    name: ContentBlockerName


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
    content_classifiers: list[TaggerConfig] | None = Field(None, description="Content classifiers to enable.")
    content_blockers: list[ConstraintConfig] | None = Field(None, description="Content blockers to enable.")

    @overload
    def dump_for_headers(self, mode: Literal["json_str"] = ...) -> str: ...
    @overload
    def dump_for_headers(self, mode: Literal["json"]) -> dict: ...

    def dump_for_headers(self, mode: Literal["json", "json_str"] = "json_str") -> dict | str:
        """Serialize for use as the ``X-Features`` HTTP header value."""
        if mode == "json":
            return self.model_dump(mode="json", exclude_none=True)
        elif mode == "json_str":
            return self.model_dump_json(exclude_none=True)
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
    ) -> "FeaturesHeader":
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
    ) -> "FeaturesHeader":
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
    ) -> "FeaturesHeader":
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
    producers: set[str] = Field(default_factory=set, description="Producer identifiers for control flow policy.")
    tags: set[str] = Field(default_factory=set, description="Tag identifiers for control flow policy.")
    consumers: set[str] = Field(default_factory=set, description="Consumer identifiers for control flow policy.")


class InternalPolicyPresets(BaseModel):
    """Internal policy presets for advanced policy configuration."""

    model_config = ConfigDict(extra="forbid")

    default_allow: bool = Field(default=True, description="Whether to allow tool calls by default.")
    default_allow_enforcement_level: Literal["hard", "soft"] = Field(
        default="soft", description="Enforcement level for default allow/deny policies."
    )
    enable_non_executable_memory: bool = Field(
        default=True, description="Attach non-executable tag to all tool results by default."
    )
    branching_meta_policy: ControlFlowMetaPolicy = Field(
        default_factory=ControlFlowMetaPolicy,
        description="Control flow meta policy for branching tools.",
    )
    enable_llm_blocked_tag: bool = Field(
        default=True,
        description="Deny tool calls to parse_with_ai if any argument has LLM_BLOCKED_TAG.",
    )
    llm_blocked_tag_enforcement_level: Literal["hard", "soft"] = Field(
        default="hard", description="Enforcement level for LLM blocked tag policy."
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
    codes: PolicyCode | None = Field(default=None, description="The security policy codes.")
    auto_gen: bool | None = Field(
        default=None, description="If True, enable auto-generation mode which relaxes certain policy constraints."
    )
    fail_fast: bool | None = Field(default=None, description="Whether to fail fast on policy violations.")
    presets: InternalPolicyPresets | None = Field(default=None, description="Internal policy presets configuration.")

    @overload
    def dump_for_headers(self, mode: Literal["json_str"] = ...) -> str: ...
    @overload
    def dump_for_headers(self, mode: Literal["json"]) -> dict: ...

    def dump_for_headers(self, mode: Literal["json", "json_str"] = "json_str") -> dict | str:
        """Serialize for use as the ``X-Policy`` HTTP header value."""
        if mode == "json":
            return self.model_dump(mode="json", exclude_none=True)
        elif mode == "json_str":
            return self.model_dump_json(exclude_none=True)
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
    ) -> "SecurityPolicyHeader":
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
    ) -> "SecurityPolicyHeader":
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

InternalSqrtToolIdType: TypeAlias = Literal["parse_with_ai", "verify_hypothesis"]
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
    min_num_tools_for_filtering: int | None = None
    clear_session_meta: Literal["never", "every_attempt", "every_turn"] | None = None
    max_n_turns: int | None = None

    # Dual-LLM only
    allow_history_mismatch: bool | None = None
    clear_history_every_n_attempts: int | None = None
    disable_rllm: bool | None = None
    enable_multistep_planning: bool | None = None
    enabled_internal_tools: list[InternalSqrtToolIdType] | None = None
    prune_failed_steps: bool | None = None
    force_to_cache: list[str] | None = None
    max_pllm_steps: int | None = None
    max_pllm_failed_steps: int | None = None
    max_tool_calls_per_step: int | None = None
    reduced_grammar_for_rllm_review: bool | None = None
    retry_on_policy_violation: bool | None = None
    wrap_tool_result: bool | None = None
    detect_tool_errors: Literal["none", "regex", "llm"] | None = None
    detect_tool_error_regex_pattern: str | None = None
    detect_tool_error_max_result_length: int | None = None
    strict_tool_result_parsing: bool | None = None


class PllmPromptOverrides(BaseModel):
    """Overrideable PLLM prompt fields."""

    model_config = ConfigDict(extra="forbid")

    flavor: PromptFlavor | None = None
    version: PromptVersion | None = None
    clarify_ambiguous_queries: bool | None = None
    context_var_visibility: Literal["none", "basic-notext", "basic-executable", "all-executable", "all"] | None = None
    query_inline_roles: list[Literal["assistant", "tool", "developer", "system"]] | None = None
    query_role_name_overrides: dict[MessageRoleType, MessageRoleType] | None = None
    query_include_tool_calls: bool | None = None
    query_include_tool_args: bool | None = None
    query_include_tool_results: bool | None = None
    debug_info_level: DebugInfoLevel | None = None


class RllmPromptOverrides(BaseModel):
    """Overrideable RLLM prompt fields."""

    model_config = ConfigDict(extra="forbid")

    flavor: PromptFlavor | None = None
    version: PromptVersion | None = None
    debug_info_level: DebugInfoLevel | None = None


class TllmPromptOverrides(BaseModel):
    """Overrideable TLLM (tool-formulating LLM) prompt fields."""

    model_config = ConfigDict(extra="forbid")

    flavor: PromptFlavor | None = None
    version: PromptVersion | None = None
    add_tool_description: bool | None = None
    add_tool_input_schema: bool | None = None


class LlmPromptOverrides(BaseModel):
    """Base overrides for other LLM types (GRLLM, QLLM, etc.)."""

    model_config = ConfigDict(extra="forbid")

    flavor: PromptFlavor | None = None
    version: PromptVersion | None = None


class PromptOverrides(BaseModel):
    """Prompt overrides for all LLMs."""

    model_config = ConfigDict(extra="forbid")

    pllm: PllmPromptOverrides | None = None
    rllm: RllmPromptOverrides | None = None
    grllm: LlmPromptOverrides | None = None
    qllm: LlmPromptOverrides | None = None
    tllm: TllmPromptOverrides | None = None
    tagllm: LlmPromptOverrides | None = None
    policy_llm: LlmPromptOverrides | None = None
    error_detector_llm: LlmPromptOverrides | None = None


class ResponseFormatOverrides(BaseModel):
    """Overrideable response-format fields (dual-llm only)."""

    model_config = ConfigDict(extra="forbid")

    strip_response_content: bool | None = None
    include_program: bool | None = None
    include_policy_check_history: bool | None = None
    include_namespace_snapshot: bool | None = None


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

    fsm: FsmOverrides | None = None
    prompt: PromptOverrides | None = None
    response_format: ResponseFormatOverrides | None = None

    @overload
    def dump_for_headers(self, mode: Literal["json_str"] = ...) -> str: ...
    @overload
    def dump_for_headers(self, mode: Literal["json"]) -> dict: ...

    def dump_for_headers(self, mode: Literal["json", "json_str"] = "json_str") -> dict | str:
        """Serialize for use as the ``X-Config`` HTTP header value."""
        if mode == "json":
            return self.model_dump(mode="json", exclude_none=True)
        elif mode == "json_str":
            return self.model_dump_json(exclude_none=True)
        else:
            raise ValueError(f"Unsupported mode for dump_for_headers: {mode}")

    @classmethod
    def single_llm(
        cls,
        min_num_tools_for_filtering: int | None = 10,
        clear_session_meta: Literal["never", "every_attempt", "every_turn"] = "never",
        max_n_turns: int | None = 50,
    ) -> "FineGrainedConfigHeader":
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
    ) -> "FineGrainedConfigHeader":
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
