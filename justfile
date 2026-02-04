local-test:
    uv run --env-file .env.local pytest

local-docs: sync-all
    uv run mkdocs serve --livereload

format:
    uv run ruff format src/ test/

lint:
    uv run ruff format --check
    uv run ty check --exclude "examples/**" --exclude "test/**" src/

sync-all:
    uv sync --all-groups