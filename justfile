local-test:
    uv run --env-file .env.local pytest

local-docs:
    uv run mkdocs serve

format:
    uv run ruff format src/ test/