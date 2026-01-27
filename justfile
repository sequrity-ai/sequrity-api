local-test:
    uv run --env-file .env.local pytest

local-docs: sync-all
    uv run mkdocs serve --livereload --dev-addr=localhost:8001

format:
    uv run ruff format src/ test/

sync-all:
    uv sync --all-groups