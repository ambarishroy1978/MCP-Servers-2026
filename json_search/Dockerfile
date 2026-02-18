# Multi-stage build for optimized final image
FROM python:3.12-slim AS builder

# Set working directory for build stage
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/app/.local/bin:$PATH

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create a non-root user with specific UID/GID for security
RUN groupadd -r -g 1001 app && \
    useradd -r -g app -u 1001 -m -d /home/app -s /bin/bash app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/app/.local

# Copy application code with proper ownership
COPY --chown=app:app src/ ./src/
COPY --chown=app:app framework/ ./framework/
COPY --chown=app:app run_server.py .
COPY --chown=app:app pyproject.toml .

# Copy environment template (users should mount actual .env or set env vars)
COPY --chown=app:app .env.example ./

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R app:app /app/logs

# Switch to non-root user
USER app

# Expose the ports used by the application
EXPOSE 8000 8001

# Health check to ensure the service is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Default command to run the server
CMD ["python", "run_server.py"]
