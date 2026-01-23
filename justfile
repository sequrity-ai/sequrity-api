local-test:
    uv run --env-file .env.local pytest

local-docs: sync-all
    uv run mkdocs serve

format:
    uv run ruff format src/ test/

sync-all:
    uv sync --all-groups