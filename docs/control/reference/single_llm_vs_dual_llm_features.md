# Available Features in Single-LLM Architecture


Sequrity Control supports two agent architectures for tool access control: **Single-LLM** and **Dual-LLM**. The Single-LLM in Sequrity Control is designed primarily for compatibility with existing systems, providing guardrail functionalities and limited policy enforcement based on session metadata. In contrast, **Dual-LLM offers all basic & advanced security features, i.e., all features listed in [Security Features](../reference/sequrity_client/headers/features_header.md), [Security Policies](../reference/sequrity_client/headers/policy_header.md), and [Fine-Grained Configurations](../reference/sequrity_client/headers/config_header.md)**.

??? question "What is Single-LLM vs. Dual-LLM?"

    Read the conceptual guide on [Single-LLM vs. Dual-LLM Agents](../learn/single-vs-dual-llm.md) to understand the differences between these architectures and their security implications.

## Supported Features of Single-LLM

Single-LLM supports a limited subset of features compared to Dual-LLM mode. The following table summarizes the feature availability in Single-LLM mode:

- [Security Features](../reference/sequrity_client/headers/features_header.md) / [X-Features](../reference/rest_api/headers/security_features.md)
    - :white_check_mark: `toxicity_filter`
    - :white_check_mark: `pii_redaction`
    - :white_check_mark: `healthcare_topic_guardrail`
    - :white_check_mark: `finance_topic_guardrail`
    - :white_check_mark: `url_blocker`
    - :white_check_mark: `file_blocker`

- [Security Policies](../reference/sequrity_client/headers/policy_header.md) / [X-Policy](../reference/rest_api/headers/security_policy.md)
    - :white_check_mark: `mode`
    - :white_check_mark: `codes`
    - :no_entry: `auto_gen`
    - :white_check_mark: `fail_fast`
    - `presets`
        - :white_check_mark: `default_allow`
        - :white_check_mark: `default_allow_enforcement_level`
        - :no_entry: `enable_non_executable_memory`
        - :white_check_mark: `enable_llm_blocked_tag`
        - :white_check_mark: `llm_blocked_tag_enforcement_level`
        - :no_entry: `branching_meta_policy`

    !!! warning "Limited Policy Enforcement in Single-LLM"

        For Single-LLM, there is no program execution and metadata propagation, so the security policies for Single-LLM must rely on

        - [Tool arguments](../learn/sqrt/00_metadata.md#tool-call-metadata-checks)
        - [Tool results wrapped in metadata](../learn/sqrt/00_metadata.md#wrapping-tool-results-with-metadata)
        - [Session metadata](../learn/sqrt/00_metadata.md#session-metadata)

- [Fine-Grained Configurations](../reference/sequrity_client/headers/config_header.md) / [X-Config](../reference/rest_api/headers/security_config.md)
    - `fsm` (shared):
        - :white_check_mark: `min_num_tools_for_filtering`
        - :white_check_mark: `clear_session_meta`
        - :white_check_mark: `max_n_turns`
    - `fsm` (dual-llm only - all :no_entry: in single-llm):
        - :no_entry: `max_pllm_steps`
        - :no_entry: `max_tool_calls_per_step`
        - :no_entry: `clear_history_every_n_attempts`
        - :no_entry: `retry_on_policy_violation`
        - :no_entry: `disable_rllm`
        - :no_entry: `reduced_grammar_for_rllm_review`
        - :no_entry: `enable_multistep_planning`
        - :no_entry: `prune_failed_steps`
        - :no_entry: `enabled_internal_tools`
        - :no_entry: `force_to_cache`
    - `prompt`:
        - :no_entry: All prompt overrides (dual-llm only)
    - `response_format`:
        - :no_entry: All response format overrides (dual-llm only)
