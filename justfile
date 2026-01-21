local-test:
    uv run --env-file .env.local pytest

format:
    uv run ruff format src/ test/