#!/bin/bash
# Getting Started with Sequrity Control API - REST API Examples

# Prerequisites:
# - A Sequrity API key (from your dashboard at sequrity.ai)
# - An LLM provider API key (e.g., OpenAI, OpenRouter)

# --8<-- [start:setup_env_vars]
SEQURITY_API_KEY="${SEQURITY_API_KEY:-your-sequrity-api-key}"
OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-your-openrouter-key}"
SERVICE_PROVIDER="openrouter"
REST_API_URL="https://api.sequrity.ai/control/chat/${SERVICE_PROVIDER}/v1/chat/completions"
# --8<-- [end:setup_env_vars]

# If SEQURITY_BASE_URL is set, use it instead of the default.
if [ -n "$SEQURITY_BASE_URL" ]; then
  REST_API_URL="${SEQURITY_BASE_URL}/control/chat/${SERVICE_PROVIDER}/v1/chat/completions"
fi

# =============================================================================
# First Message Example
# =============================================================================

echo "=== First Message Example ==="
# --8<-- [start:first_message]
curl -X POST $REST_API_URL \
  -H "Authorization: Bearer $SEQURITY_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $OPENROUTER_API_KEY" \
  -d '{
    "model": "openai/gpt-5-mini",
    "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
  }'
# --8<-- [end:first_message]
echo

# =============================================================================
# Single-LLM
# =============================================================================

echo "=== Single LLM Mode ==="

# Only X-Features is needed to select the architecture.
# X-Policy and X-Config are optional — the server uses preset defaults.
# --8<-- [start:single_llm]
curl -X POST $REST_API_URL \
  -H "Authorization: Bearer $SEQURITY_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $OPENROUTER_API_KEY" \
  -H 'X-Features: {"agent_arch":"single-llm"}' \
  -d '{
    "model": "openai/gpt-5-mini",
    "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
  }'
# --8<-- [end:single_llm]
echo

# =============================================================================
# Dual-LLM
# =============================================================================

echo "=== Dual LLM ==="

# --8<-- [start:dual_llm]
curl -X POST $REST_API_URL \
  -H "Authorization: Bearer $SEQURITY_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $OPENROUTER_API_KEY" \
  -H 'X-Features: {"agent_arch":"dual-llm"}' \
  -d '{
    "model": "openai/gpt-5-mini",
    "messages": [{"role": "user", "content": "What is the largest prime number below 100?"}]
  }'
# --8<-- [end:dual_llm]
