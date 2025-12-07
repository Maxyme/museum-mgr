# syntax=docker.io/docker/dockerfile-upstream:1.19.0-labs
FROM ghcr.io/astral-sh/uv:0.9.7-trixie-slim@sha256:7405046f73328d273a6f1d347549db9981de7c163c9ce5df3f7eda225bdf424b AS builder

# Set uv Python install directory
ENV UV_PYTHON_INSTALL_DIR=/python

# Install Python
RUN uv python install 3.13

WORKDIR /app

# Copy pyproject.toml
COPY pyproject.toml .

# Install dependencies
RUN uv sync --no-install-project --compile-bytecode --link-mode copy

# Runtime image
FROM debian:trixie-slim@sha256:a347fd7510ee31a84387619a492ad6c8eb0af2f2682b916ff3e643eb076f925a

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy Python from the build stage
COPY --from=builder --chown=python:python /python /python
# Copy the .venv from the builder
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

COPY . .

CMD ["pytest", "-v"]

