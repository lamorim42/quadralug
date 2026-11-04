# Build com contexto na raiz do repositório (door 1).
FROM python:3.13-slim

ENV UV_PYTHON_DOWNLOADS=never UV_COMPILE_BYTECODE=1
RUN pip install --no-cache-dir uv==0.13.6

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages/observability/pyproject.toml packages/observability/pyproject.toml
COPY services/backend/pyproject.toml services/backend/pyproject.toml
COPY services/bff/pyproject.toml services/bff/pyproject.toml
RUN uv sync --frozen --no-dev --no-install-workspace --package quadralug-backend

COPY packages/observability/ packages/observability/
COPY services/backend/ services/backend/
RUN uv sync --frozen --no-dev --no-editable --package quadralug-backend

RUN useradd --uid 10001 --no-create-home app
USER 10001

ENV PATH=/app/.venv/bin:$PATH
CMD ["python", "-m", "quadralug_backend"]
