# syntax=docker.io/docker/dockerfile-upstream:1.14.0-labs
# Build python dependencies
FROM python:3.13.7-bookworm@sha256:c900d35aba5fe4c1dc1cd358408baae2902ff2a2926a1d15cc5002c6061ddb2e AS build
ENV PYTHONUNBUFFERED=1
ENV UV_VERSION=0.5.16

WORKDIR /app
RUN pip install --no-cache-dir uv==${UV_VERSION}

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --compile-bytecode --link-mode copy

# Build runtime image
FROM python:3.13.7-slim-bookworm@sha256:adafcc17694d715c905b4c7bebd96907a1fd5cf183395f0ebc4d3428bd22d92d AS runtime
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Create user to run app
RUN <<EOT
groupadd -r app
useradd -r -d /app -g app -N app
EOT

# Copy venv from build and add to path
COPY --from=build --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy app code
COPY --exclude=uv.lock --chown=app:app . /app

# Set user to run app
USER app

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]

