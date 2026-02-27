# SequrityClient API Reference

This section provides the API reference for `SequrityClient`, the Python interface for Sequrity's Control API.

## Overview

The Control API enables secure LLM interactions with policy enforcement. Key capabilities:

- **Chat Completions**: OpenAI-compatible chat API with security features (toxicity filtering, PII redaction, topic guardrails)
- **Responses API**: OpenAI Responses API with function calling, multi-turn, reasoning, and streaming support
- **Anthropic Messages**: Anthropic Messages API with security features
- **LangGraph Integration**: Execute LangGraph workflows with security policies via Sequrity's Dual-LLM runtime
- **Policy Generation**: Generate SQRT policies from natural language descriptions

## API Modules

| Module | Description |
|--------|-------------|
| [Chat Completion](chat_completion.md) | Chat completion API, request/response types, and result schemas |
| [Responses API](responses.md) | OpenAI Responses API, request/response types, and streaming events |
| [Anthropic Messages](message.md) | Anthropic Messages API, request/response types |
| [LangGraph sequrity mode](langgraph.md) | LangGraph execution API and related types |
| [Policy Generation](policy_gen.md) | Generate SQRT policies from natural language |
| [ValueWithMeta](value_with_meta.md) | Value wrapper with metadata for policy enforcement |
| [SQRT](sqrt.md) | SQRT policy parser and utilities |
| [Integrations - LangGraph](integrations/integrations_langgraph.md) | LangChain/LangGraph framework integration |
| [Integrations - OAI Agents SDK](integrations/integrations_oai_sdk.md) | OpenAI Agents SDK framework integration |

### Headers

Configuration headers for customizing security behavior:

- **[FeaturesHeader](headers/features_header.md)** - Enable/disable security features
- **[PolicyHeader](headers/policy_header.md)** - Define SQRT policies for tool access control
- **[ConfigHeader](headers/config_header.md)** - Fine-grained security configuration



::: sequrity._client.SequrityClient
    options:
      show_root_heading: true
      show_source: false
      members: ["control"]
