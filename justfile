test_target := "test/"

local-test target=test_target:
    uv run --env-file .env.local pytest {{target}}

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