lint:
    uv run ruff format . --check
    uv run ruff check .

format:
    uv run ruff format .

test:
    uv run pytest tests/ -v

test-all:
    uv run pytest tests/ -v

start-api:
    # Start api with litestar for debugging
    uv run litestar run

build:
    docker build -t museum-mgr .

run-docker population="10000":
    docker run -v {{justfile_directory()}}/cache:/app/cache museum-mgr {{population}}

create-migration MESSAGE:
    uv run alembic revision --autogenerate -m "{{MESSAGE}}"

migrate:
    uv run alembic upgrade head

clear-db:
    uv run python manage_db.py clear
