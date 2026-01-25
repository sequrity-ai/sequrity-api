#!/bin/bash
# Getting Started with Sequrity Control API - REST API Examples

# Prerequisites:
# - A Sequrity API key (from your dashboard at sequrity.ai)
# - An LLM provider API key (e.g., OpenAI, OpenRouter)

SEQURITY_API_KEY="${SEQURITY_API_KEY:-your-sequrity-api-key}"
OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-your-openrouter-key}"

# =============================================================================
# Single-LLM
# =============================================================================
# Single-LLM passes your request directly to the LLM with optional
# security taggers and constraints.

echo "=== Single LLM Mode ==="

# --8<-- [start:single_llm]
curl -X POST https://api.sequrity.ai/control/v1/chat/completions \
  -H "Authorization: Bearer $SEQURITY_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $OPENROUTER_API_KEY" \
  -H 'X-Security-Policy: {"language":"sqrt-lite","codes":""}' \
  -H 'X-Security-Features: [{"feature_name":"Single LLM","config_json":"{\"mode\":\"standard\"}"},{"feature_name":"Long Program Support","config_json":"{\"mode\":\"base\"}"}]' \
  -d '{
    "model": "openai/gpt-5-mini",
    "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
  }'
# --8<-- [end:single_llm]

# =============================================================================
# Dual-LLM
# =============================================================================
# Dual-LLM uses a planning LLM to generate secure execution plans on which
# security policies and features are enforced. This provides stronger security
# guarantees for agentic use cases.

echo "=== Dual LLM ==="

# --8<-- [start:dual_llm]
curl -X POST https://api.sequrity.ai/control/v1/chat/completions \
  -H "Authorization: Bearer $SEQURITY_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $OPENROUTER_API_KEY" \
  -H 'X-Security-Policy: {"language":"sqrt-lite","codes":""}' \
  -H 'X-Security-Features: [{"feature_name":"Dual LLM","config_json":"{\"mode\":\"standard\"}"},{"feature_name":"Long Program Support","config_json":"{\"mode\":\"base\"}"}]' \
  -d '{
    "model": "openai/gpt-5-mini",
    "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
  }'
# --8<-- [end:dual_llm]
