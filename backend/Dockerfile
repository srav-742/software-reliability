# Build Stage
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Final Runtime Stage
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from builder stage
COPY --from=builder /install /usr/local

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app

COPY . /app

RUN chmod +x /app/entrypoint.sh
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

