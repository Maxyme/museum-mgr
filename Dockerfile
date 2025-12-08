# syntax=docker.io/docker/dockerfile-upstream:1.19.0-labs
# Build image
FROM ghcr.io/astral-sh/uv:0.9.7-trixie-slim@sha256:7405046f73328d273a6f1d347549db9981de7c163c9ce5df3f7eda225bdf424b AS builder

# Copy .python-version file to set Python version
COPY .python-version .python-version

# Set uv Python install directory
ENV UV_PYTHON_INSTALL_DIR=/python

# Install Python to specified directory
RUN uv python install

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev  --compile-bytecode --link-mode copy

# Runtime image
FROM debian:trixie-slim@sha256:a347fd7510ee31a84387619a492ad6c8eb0af2f2682b916ff3e643eb076f925a AS run

# Disable output buffering for stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set the workdir
WORKDIR /app

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy Python from the build stage
COPY --from=builder --chown=python:python /python /python

# Copy the .venv from the builder
COPY --from=builder --chown=nonroot:nonroot .venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use the non-root user to run application
USER nonroot

# Copy the application from the builder
COPY . /app

ENTRYPOINT ["python", "main.py"]