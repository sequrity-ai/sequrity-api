#!/bin/bash
# Getting Started with Sequrity Control API - REST API Examples

# Prerequisites:
# - A Sequrity API key (from your dashboard at sequrity.ai)
# - An LLM provider API key (e.g., OpenAI, OpenRouter)

# --8<-- [start:setup_env_vars]
SEQURITY_API_KEY="${SEQURITY_API_KEY:-your-sequrity-api-key}"
OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-your-openrouter-key}"
SERVICE_PROVIDER="openrouter"
# --8<-- [end:setup_env_vars]

# =============================================================================
# First Message Example
# =============================================================================

echo "=== First Message Example ==="
# --8<-- [start:first_message]
curl -X POST https://api.sequrity.ai/control/${SERVICE_PROVIDER}/v1/chat/completions \
  -H "Authorization: Bearer $SEQURITY_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $OPENROUTER_API_KEY" \
  -d '{
    "model": "openai/gpt-5-mini",
    "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
  }'
# --8<-- [end:first_message]

# =============================================================================
# Single-LLM
# =============================================================================

echo "=== Single LLM Mode ==="

# --8<-- [start:single_llm]
curl -X POST https://api.sequrity.ai/control/${SERVICE_PROVIDER}/v1/chat/completions \
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

echo "=== Dual LLM ==="

# --8<-- [start:dual_llm]
curl -X POST https://api.sequrity.ai/control/${SERVICE_PROVIDER}/v1/chat/completions \
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
