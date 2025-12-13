lint:
    uv run ruff format . --check
    uv run ruff check .

format:
    uv run ruff format .

test:
    uv run pytest tests/ -v

test-functional:
    docker compose up -d db
    uv run python manage_db.py wait
    just migrate
    docker compose up -d api worker
    cd api_tester && API_URL="http://localhost:8000" uv run pytest test_e2e.py

test-all:
    uv run pytest tests/ -v

start-api:
    # Start api with litestar for debugging
    uv run litestar run

start-worker:
     pgq run worker_app:main

build:
    docker build -t museum-mgr .

run-docker population="10000":
    docker run -v {{justfile_directory()}}/cache:/app/cache museum-mgr {{population}}

start-services:
    docker compose up db -d

create-migration MESSAGE:
    uv run alembic revision --autogenerate -m "{{MESSAGE}}"

migrate:
    uv run alembic upgrade head
    uv run python manage_db.py install-queue

clear-db:
    uv run python manage_db.py clear
