# --------------------
# Stage 1: Builder
# --------------------
FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv via pip (lighter than curl script)
RUN pip install --no-cache-dir uv

WORKDIR /code

COPY pyproject.toml uv.lock ./

# Install deps into project .venv (isolated, no cache needed later)
RUN uv sync --frozen --no-dev

# --------------------
# Stage 2: Runtime
# --------------------
FROM python:3.13-slim AS runtime

WORKDIR /code

# Copy uv from builder and install it in runtime stage
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /usr/local/lib/python3.13/site-packages/uv /usr/local/lib/python3.13/site-packages/uv
COPY --from=builder /code/.venv /code/.venv

# Copy source
COPY . .
COPY app.env .env

# Collect static files at build
RUN uv run --frozen manage.py collectstatic --noinput

# Default command (can override in docker-compose)
CMD ["uv", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "config.asgi:application", "--bind", "0.0.0.0:8000", "-w", "4"]
