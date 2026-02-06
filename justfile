test_target := "test/"

local-test target=test_target:
    uv run --group agents --env-file .env.local pytest {{target}}

# Run all example scripts to test if they work
test-examples:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "🧪 Testing all examples..."
    echo ""

    echo "📚 Getting Started Examples"
    uv run --group examples --env-file .env.local python examples/control/getting_started/first_message/sequrity_client.py
    uv run --group examples --env-file .env.local python examples/control/getting_started/tool_use_dual_llm/rest_api.py
    uv run --group examples --env-file .env.local python examples/control/getting_started/tool_use_dual_llm/sequrity_client.py
    uv run --group examples --group langgraph --env-file .env.local python examples/control/getting_started/langgraph/sequrity_client.py

    echo ""
    echo "🔌 Integration Examples"
    uv run --group examples --group langgraph --env-file .env.local python examples/control/integrations/langgraph_basic.py
    uv run --group examples --group agents --env-file .env.local python examples/control/integrations/openai_agents_sdk_basic.py

    echo ""
    echo "🔒 Advanced SQRT Examples"
    uv run --group examples --env-file .env.local python examples/control/advanced_sqrt_examples/rest_api.py
    uv run --group examples --env-file .env.local python examples/control/advanced_sqrt_examples/sequrity_client.py

    echo ""
    echo "📖 SQRT Learning Examples"
    uv run --env-file .env.local python examples/control/learn_sqrt/basic_types.py
    uv run --env-file .env.local python examples/control/learn_sqrt/metadata.py
    uv run --env-file .env.local python examples/control/learn_sqrt/predicates.py
    uv run --env-file .env.local python examples/control/learn_sqrt/set_operations.py
    uv run --env-file .env.local python examples/control/learn_sqrt/tool_policies.py

    echo ""
    echo "✅ All examples completed successfully!"

serve-docs: sync-docs
    uv run mike serve --dev-addr=localhost:8001

# Deploy docs for the latest git tag (e.g., v0.1.0 → 0.1.0)
deploy-docs: sync-docs
    uv run mike deploy --update-aliases $(git describe --tags --abbrev=0 --match 'v*' | sed 's/^v//') latest
    uv run mike set-default latest

format:
    uv run ruff format src/ test/

lint:
    uv run ruff format --check
    uv run ty check --exclude "examples/**" --exclude "test/**" src/

sync-all:
    uv sync --all-groups

sync-docs:
    uv sync --group docs

setup-dev:
    uv sync --all-groups