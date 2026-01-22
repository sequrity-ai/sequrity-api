# Sequrity Control Examples - Release 2024-01-22

This guide demonstrates the capabilities of **Sequrity Control** through practical examples. These examples showcase how the Dual-LLM architecture provides architectural security guarantees that traditional guardrail systems cannot match.

## Overview

Sequrity Control uses a "Plan-Then-Execute" architecture that creates a formal separation between understanding instructions and acting on data:

1. **Planner LLM**: Reads your prompt and creates a safe, step-by-step plan
2. **Security Checkpoint**: Intercepts and validates the plan against your defined policies before any action is taken
3. **Secure Execution**: Only vetted, secure steps are executed while malicious instructions are identified as data and ignored

## Examples Covered

The examples notebook demonstrates five key use cases:

### 1. Preventing Sensitive Data Leaks
Configure policies to prevent confidential documents from being sent to untrusted email addresses while allowing trusted recipients. Uses data tagging and regex-based domain matching.

### 2. Enforcing Complex Business Logic
Implement stateful, multi-step business rules such as requiring multiple refund requests before approval. Demonstrates session-based meta tracking and policy enforcement.

### 3. Ensuring Factual Accuracy with Data Provenance
Enforce that AI outputs are grounded in verified sources by tracking data provenance. Prevents hallucinated or unverified data from being used in critical operations.

### 4. Enforcing Legal and Compliance Mandates
Ensure PII data is properly de-identified before being shared with external parties. Uses tag-based policies to enforce data privacy regulations.

### 5. Audit, Fairness, Transparency, and Interpretability
Prevent discriminatory decision-making by blocking control flow based on protected attributes (e.g., race). Includes policies for both branching control flow and AI parsing restrictions.

## Download

The examples are available in three formats:

| Format | Description | Download |
|--------|-------------|----------|
| **Jupyter Notebook** | Interactive notebook with full explanations and outputs | [control-release-examples.ipynb](https://github.com/sequrity-ai/sequrity-api/blob/main/docs/control/examples/control-release-examples.ipynb) |
| **REST API Script** | Python script using direct REST API calls | [control-release-examples-rest-api.py](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/release-examples/control-release-examples-rest-api.py) |
| **Sequrity Client Script** | Python script using the Sequrity Python client | [control-release-examples-sequrity-client.py](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/release-examples/control-release-examples-sequrity-client.py) |

## Getting Started

Before running the examples, ensure you have:

1. An OpenRouter or OpenAI API key
2. A Sequrity API key (obtain from [sequrity.ai](https://sequrity.ai))
3. Python 3.10+ with the required dependencies

Set your environment variables:

```bash
export OPENROUTER_API_KEY="your-openrouter-key"
export SEQURITY_API_KEY="your-sequrity-key"
```

Then proceed to the [interactive notebook](control-release-examples.ipynb) to explore the examples in detail.
