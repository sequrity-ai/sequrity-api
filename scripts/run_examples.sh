#!/usr/bin/env bash
set -euo pipefail
echo "🧪 Testing all examples..."
echo ""

echo "📚 Getting Started Examples"
uv run --group examples "$@" python examples/control/getting_started/first_message/sequrity_client.py
uv run --group examples "$@" python examples/control/getting_started/tool_use_dual_llm/rest_api.py
uv run --group examples "$@" python examples/control/getting_started/tool_use_dual_llm/sequrity_client.py
uv run --group examples --group langgraph "$@" python examples/control/getting_started/langgraph/sequrity_client.py
uv run --group examples "$@" python examples/control/getting_started/custom_headers/rest_api.py
uv run --group examples "$@" python examples/control/getting_started/custom_headers/sequrity_client.py

echo ""
echo "🔌 Integration Examples"
uv run --group examples --group langgraph "$@" python examples/control/integrations/langgraph_basic.py
uv run --group examples --group agents "$@" python examples/control/integrations/openai_agents_sdk_basic.py

echo ""
echo "🔒 Advanced SQRT Examples"
uv run --group examples "$@" python examples/control/advanced_sqrt_examples/rest_api.py
uv run --group examples "$@" python examples/control/advanced_sqrt_examples/sequrity_client.py

echo ""
echo "📖 SQRT Learning Examples"
uv run --group examples "$@" python examples/control/learn_sqrt/basic_types.py
uv run --group examples "$@" python examples/control/learn_sqrt/metadata.py
uv run --group examples "$@" python examples/control/learn_sqrt/predicates.py
uv run --group examples "$@" python examples/control/learn_sqrt/set_operations.py
uv run --group examples "$@" python examples/control/learn_sqrt/tool_policies.py

echo ""
echo "✅ All examples completed successfully!"
