# Multi-stage build for smaller final image
FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and install package (knowledge_base is excluded via .dockerignore)
COPY . .
RUN pip install --no-cache-dir -e .

# Runtime stage
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app

# Install only runtime dependencies (libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy only application code needed at runtime (knowledge_base excluded via .dockerignore)
COPY bitcoin_agent ./bitcoin_agent
COPY alembic ./alembic
COPY alembic.ini .
COPY pyproject.toml .

# Verify package structure
RUN python -c "import bitcoin_agent; import bitcoin_agent.models; import bitcoin_agent.services; print('✓ Package structure verified')"

EXPOSE 8000

# Support PORT env variable (Railway, Render, etc.)
# Defaults to 8000 if PORT is not set
CMD ["sh", "-c", "uvicorn bitcoin_agent.api.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]