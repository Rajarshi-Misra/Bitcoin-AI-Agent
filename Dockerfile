FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Verify package structure (skip config-dependent imports)
RUN python -c "import bitcoin_agent; import bitcoin_agent.models; import bitcoin_agent.services; print('✓ Package structure verified')"

EXPOSE 8000

# Support PORT env variable (Railway, Render, etc.)
# Defaults to 8000 if PORT is not set
CMD ["sh", "-c", "uvicorn bitcoin_agent.api.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]