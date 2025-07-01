# NetApp ActiveIQ MCP Server - Multi-stage Docker build
FROM python:3.10-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Labels for container metadata
LABEL org.opencontainers.image.title="NetApp ActiveIQ MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol server for NetApp ActiveIQ Unified Manager"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.vendor="NetApp Integration"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY mcp_requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /tmp/mcp_requirements.txt

# Production stage
FROM python:3.10-slim as production

# Create non-root user for security
RUN groupadd -r mcp && useradd -r -g mcp -d /app -s /bin/bash mcp

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=mcp:mcp mcp_server.py .
COPY --chown=mcp:mcp start_mcp_server.py .
COPY --chown=mcp:mcp test_mcp_server.py .

# Create directories for logs and temp files
RUN mkdir -p /app/logs /app/tmp && chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; import sys; sys.exit(0)"

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port for health checks and monitoring
EXPOSE 8080

# Default command
CMD ["python", "start_mcp_server.py"]
