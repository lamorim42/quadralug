# Build com contexto na raiz do repositório (door 1).
FROM python:3.13-slim

ENV UV_PYTHON_DOWNLOADS=never
RUN pip install --no-cache-dir uv==0.13.6

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages/observability/ packages/observability/
COPY services/backend/pyproject.toml services/backend/pyproject.toml
COPY services/bff/ services/bff/
RUN uv sync --frozen --no-dev --no-editable --package quadralug-bff

RUN useradd --uid 10001 --no-create-home app
USER 10001

ENV PATH=/app/.venv/bin:$PATH
CMD ["python", "-m", "quadralug_bff"]
