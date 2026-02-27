test_target := "test/"

local-test target=test_target:
    uv run --group agents --env-file .env.local pytest {{ target }}

# Run all example scripts to test if they work
test-examples:
    bash scripts/run_examples.sh --env-file .env.local

serve-docs: sync-docs
    uv run mkdocs serve --dev-addr=localhost:8001

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
