# SequrityClient.control API Reference

This section provides the API reference for `SequrityClient.control`, the Python interface for Sequrity's Control API.

## Overview

The Control API enables secure LLM interactions with policy enforcement. Key capabilities:

- **Chat Completions**: OpenAI-compatible chat API with security features (toxicity filtering, PII redaction, topic guardrails)
- **LangGraph Integration**: Execute LangGraph workflows with security policies via Sequrity's Dual-LLM runtime

## API Modules

| Module | Description |
|--------|-------------|
| [Chat Completion](chat_completion.md) | Chat completion API, request/response types, and result schemas |
| [LangGraph](langgraph.md) | LangGraph execution API and related types |
| [Integrations](integrations_oai_sdk.md) | Framework integrations (OpenAI Agent ADK, etc.) |
| [Headers](headers/features_header.md) | Configuration headers for features, policies, and fine-grained settings |
| [ValueWithMeta](value_with_meta.md) | Value wrapper with metadata for policy enforcement |
| [SQRT](sqrt.md) | SQRT policy parser and utilities |

### Headers

Configuration headers for customizing security behavior:

- **[FeaturesHeader](headers/features_header.md)** - Enable/disable security features
- **[PolicyHeader](headers/policy_header.md)** - Define SQRT policies for tool access control
- **[ConfigHeader](headers/config_header.md)** - Fine-grained security configuration



::: sequrity.control.wrapper.ControlApiWrapper
    options:
      show_root_heading: true
      show_source: false
      members: ["create_chat_completion", "compile_and_run_langgraph"]
