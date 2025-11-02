lint:
    uv run ruff format . --check
    uv run ruff check .

format:
    uv run ruff format .

test:
    uv run pytest tests/ -v

build:
    docker build -t museum-mgr .

run-docker population="10000":
    docker run -v {{justfile_directory()}}/cache:/app/cache museum-mgr {{population}}
