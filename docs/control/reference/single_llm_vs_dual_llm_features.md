# Available Features in Single-LLM and Dual-LLM Modes

<!-- mention our single llm does roughly nothing, it directly send requests to service provider and have some guardrails. -->

Sequrity Control supports two agent architectures for tool access control: **Single-LLM** and **Dual-LLM**. The Single-LLM in Sequrity Control is designed primarily for compatibility with existing systems, providing guardrail functionalities and limited policy enforcement based on session metadata. In contrast, **Dual-LLM offers all basic & advanced security features, i.e., all features listed in [Security Features](../reference/sequrity_client/headers/features_header.md), [Security Policies](../reference/sequrity_client/headers/policy_header.md), and [Fine-Grained Configurations](../reference/sequrity_client/headers/config_header.md)**.

??? question "What is Single-LLM vs. Dual-LLM?"

    Read the conceptual guide on [Single-LLM vs. Dual-LLM Agents](../learn/single-vs-dual-llm.md) to understand the differences between these architectures and their security implications.

## Supported Features of Single-LLM

Single-LLM supports a limited subset of features compared to Dual-LLM mode. The following table summarizes the feature availability in Single-LLM mode:

- [Security Features](../reference/sequrity_client/headers/features_header.md) / [X-Security-Features](../reference/rest_api/headers/security_features.md)
    - :white_check_mark: `toxicity_filter`
    - :white_check_mark: `pii_redaction`
    - :white_check_mark: `healthcare_guardrail`
    - :white_check_mark: `finance_guardrail`
    - :white_check_mark: `legal_guardrail`
    - :white_check_mark: `url_blocker`
    - :no_entry: `long_program_mode`

- [Security Policies](../reference/sequrity_client/headers/policy_header.md) / [X-Security-Policy](../reference/rest_api/headers/security_policy.md)
    - :white_check_mark: `language`
    - :white_check_mark: `codes`
    - :white_check_mark: `auto_gen`
    - :white_check_mark: `fail_fast`
    - `internal_policy_preset`
        - :white_check_mark: `default_allow`
        - :white_check_mark: `default_allow_enforcement_level`
        - :no_entry: `enable_non_executable_memory`
        - :no_entry: `enable_llm_blocked_tag`
        - :no_entry: `branching_meta_policy`

    !!! warning "Limited Policy Enforcement in Single-LLM"

        For Single-LLM, there is no program execution and metadata propagation, so the security policies for Single-LLM must rely on

        - [Tool results wrapped in metadata](../learn/sqrt/00_metadata.md#wrapping-tool-results-with-metadata)
        - [Session metadata](../learn/sqrt/00_metadata.md#session-metadata)

- [Fine-Grained Configurations](../reference/sequrity_client/headers/config_header.md) / [X-Security-Config](../reference/rest_api/headers/security_config.md)
    - :no_entry: `max_pllm_attempts`
    - :no_entry: `merge_system_messages`
    - :no_entry: `convert_system_to_developer_messages`
    - :no_entry: `include_other_roles_in_user_query`
    - :no_entry: `max_tool_calls_per_request`
    - :no_entry: `clear_history_every_n_attempts`
    - :no_entry: `retry_on_policy_violation`
    - :no_entry: `cache_tool_result`
    - :no_entry: `force_to_cache`
    - :white_check_mark: `min_num_tools_for_filtering`
    - :white_check_mark: `clear_session_meta`
    - :no_entry: `disable_rllm`
    - :no_entry: `reduced_grammar_to_rllm_review`
    - :no_entry: `rllm_confidence_score_threshold`
    - :no_entry: `pllm_debug_info`
    - :no_entry: `max_n_turns`
    - :no_entry: `enable_multi_step_planning`
    - :no_entry: `prune_failed_steps`
    - :no_entry: `enabled_internal_tools`
    - :no_entry: `restate_user_query_before_planning`
    - :no_entry: `pllm_can_ask_for_clarification`
    - :no_entry: `reduced_grammar_version`
    - :no_entry: `response_format`
    - :no_entry: `show_pllm_secure_var_values`
