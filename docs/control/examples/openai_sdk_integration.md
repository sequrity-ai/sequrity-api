# OpenAI Agents SDK Integration

This guide demonstrates how to use Sequrity with the [OpenAI Agents SDK](https://github.com/openai/openai-agents) framework.

## Overview

The `SequrityAsyncOpenAI` client is a drop-in replacement for OpenAI's `AsyncOpenAI` client that automatically adds Sequrity's security features:

- **Dual-LLM Architecture**: Separate planning and quarantined execution
- **Automatic Session Tracking**: Maintains conversation context across requests
- **Security Headers**: Automatically injects features, policies, and configuration
- **Full OpenAI Compatibility**: Works seamlessly with OpenAI Agents SDK

## Installation

```bash
# Install sequrity-api with OpenAI support (included by default)
pip install sequrity

# Optional: Install OpenAI Agents SDK for agent framework support
pip install openai-agents
```

## Basic Setup

```python
--8<-- "examples/control/integrations/openai_agents_sdk_basic.py:basic-setup"
```

## Basic Completion

```python
--8<-- "examples/control/integrations/openai_agents_sdk_basic.py:basic-completion"
```

## Session Management

```python
--8<-- "examples/control/integrations/openai_agents_sdk_basic.py:session-management"
```

## Using with OpenAI Agents SDK

```python
--8<-- "examples/control/integrations/openai_agents_sdk_basic.py:with-agents-sdk"
```

## Complete Example

See the complete working example at [`examples/control/integrations/openai_agents_sdk_basic.py`](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/integrations/openai_agents_sdk_basic.py).

## See Also

- [FeaturesHeader Documentation](../reference/sequrity_client/headers/features_header.md)
- [SecurityPolicyHeader Documentation](../reference/sequrity_client/headers/policy_header.md)
- [FineGrainedConfigHeader Documentation](../reference/sequrity_client/headers/config_header.md)
- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents)
