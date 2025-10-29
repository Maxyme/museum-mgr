lint:
    uv run ruff format . --check
    uv run ruff check .

format:
    uv run ruff format .

test:
    uv run pytest tests/