# Multi-stage build optimized for Railway (ARM64, CPU-only)
FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies from requirements.txt only
# Install CPU-only PyTorch first (works on both x86_64 and ARM64), then rest of requirements
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    # Install CPU-only torch (smaller, no GPU deps) - sentence-transformers needs this
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Force CPU-only for PyTorch/sentence-transformers (no GPU dependencies)
    TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu

WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code (knowledge_base excluded via .dockerignore)
COPY bitcoin_agent ./bitcoin_agent
COPY alembic ./alembic
COPY alembic.ini .

# Verify critical imports work
RUN python -c "import bitcoin_agent; import sentence_transformers; print('✓ Package structure verified')"

EXPOSE 8000

# Support PORT env variable (Railway requirement)
# Defaults to 8000 if PORT is not set
CMD ["sh", "-c", "uvicorn bitcoin_agent.api.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
