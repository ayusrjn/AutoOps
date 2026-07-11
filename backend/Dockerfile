FROM python:3.12-slim AS builder

# Install uv for fast dependency syncing
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency configurations
COPY pyproject.toml uv.lock ./

# Install dependencies in a virtual environment
RUN uv sync --frozen --no-dev

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment and source code
COPY --from=builder /app/.venv /app/.venv
COPY app ./app

# Add virtual env to path
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Start Uvicorn backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
