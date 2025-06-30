# Installation Guide

Complete installation guide for the NetApp ActiveIQ MCP Server across different environments.

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 10GB available space
- **Network**: Access to NetApp ActiveIQ Unified Manager
- **OS**: Linux, macOS, or Windows (with Docker)

### Recommended Requirements
- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ available space
- **Network**: Dedicated network access to NetApp infrastructure

### Software Prerequisites
- **Docker 20.10+** or **Python 3.10+**
- **Git** (for source installation)
- **curl** (for testing)

## Installation Methods

### Method 1: Docker Installation (Recommended)

#### Pull Pre-built Image

```bash
# Pull the latest stable version
docker pull netapp/activeiq-mcp-server:latest

# Or pull a specific version
docker pull netapp/activeiq-mcp-server:v1.2.0
```

#### Build from Source

```bash
# Clone repository
git clone https://github.com/netapp/activeiq-mcp-server.git
cd activeiq-mcp-server

# Build Docker image
docker build -t netapp/activeiq-mcp-server:local .
```

### Method 2: Python Installation

#### From PyPI

```bash
# Install from PyPI (when available)
pip install netapp-activeiq-mcp-server
```

#### From Source

```bash
# Clone repository
git clone https://github.com/netapp/activeiq-mcp-server.git
cd activeiq-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Method 3: Kubernetes Installation

#### Using Helm

```bash
# Add NetApp Helm repository
helm repo add netapp https://netapp.github.io/activeiq-mcp-server
helm repo update

# Install with default values
helm install netapp-mcp-server netapp/activeiq-mcp-server

# Install with custom values
helm install netapp-mcp-server netapp/activeiq-mcp-server \
  --set netapp.umHost=your-um-host.company.com \
  --set netapp.username=admin \
  --set netapp.password=your-password
```

#### Using kubectl

```bash
# Apply Kubernetes manifests
kubectl apply -f https://raw.githubusercontent.com/netapp/activeiq-mcp-server/main/deploy/kubernetes/
```

### Method 4: Knative Functions (Serverless)

#### Prerequisites

```bash
# Install Knative CLI
curl -L https://github.com/knative/client/releases/latest/download/kn-linux-amd64 -o kn
chmod +x kn && sudo mv kn /usr/local/bin/

# Install Knative func CLI
curl -L https://github.com/knative/func/releases/latest/download/func_linux_amd64.tar.gz | tar xz
chmod +x func && sudo mv func /usr/local/bin/

# Verify installation
kn version
func version
```

#### Option A: Deploy Complete MCP Server as Function

```bash
# Create MCP server function
func create netapp-mcp-server --language python --template http
cd netapp-mcp-server

# Configure func.yaml
cat > func.yaml << 'EOF'
specVersion: 0.35.0
name: netapp-mcp-server
runtime: python
registry: your-registry.com/netapp
image: your-registry.com/netapp/netapp-mcp-server:latest
created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
invoke: gunicorn
build:
  builder: pack
  buildpacks:
    - gcr.io/paketo-buildpacks/python
run:
  env:
    - name: FUNCTION_TARGET
      value: main
deploy:
  namespace: netapp-mcp
  options:
    scale:
      min: 0
      max: 10
      metric: concurrency
      target: 100
    resources:
      requests:
        cpu: 500m
        memory: 512Mi
      limits:
        cpu: 2000m
        memory: 1Gi
    annotations:
      autoscaling.knative.dev/scaleDownDelay: "60s"
      autoscaling.knative.dev/scaleUpDelay: "0s"
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastmcp>=0.5.0
httpx>=0.25.0
pydantic>=2.0.0
python-dotenv>=1.0.0
uvicorn>=0.24.0
parliament-functions>=1.0.0
EOF

# Copy MCP server code
cp ../mcp_server.py func.py

# Deploy with environment variables
func deploy \
  --namespace netapp-mcp \
  --env NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api" \
  --env NETAPP_USERNAME="your-username" \
  --env NETAPP_PASSWORD="your-password" \
  --env NETAPP_VERIFY_SSL="false" \
  --env MCP_SERVER_PORT="8080" \
  --env MCP_LOG_LEVEL="INFO" \
  --build
```

#### Option B: Deploy Individual Function Components

```bash
# Set environment variables
export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
export NETAPP_USERNAME="your-username"
export NETAPP_PASSWORD="your-password"
export REGISTRY="your-registry.com/netapp"

# Deploy using the provided script
./scripts/deploy-knative-functions.sh
```

#### Managing Knative Functions

```bash
# List functions
kn service list -n netapp-mcp

# Get function URL
MCP_URL=$(kn service describe netapp-mcp-server -n netapp-mcp -o jsonpath='{.status.url}')
echo "MCP Server URL: $MCP_URL"

# View function logs
kn func logs netapp-mcp-server --follow

# Update function configuration
kn service update netapp-mcp-server \
  --env MCP_LOG_LEVEL=DEBUG \
  --scale-min 1 \
  --scale-max 20 \
  -n netapp-mcp

# Test function
curl -X POST $MCP_URL/tools/get_clusters \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### Traffic Management

```bash
# Deploy new version without traffic
func deploy --tag v2 --no-traffic

# Split traffic between versions
kn service update netapp-mcp-server \
  --traffic v1=90,v2=10 \
  -n netapp-mcp

# Promote new version
kn service update netapp-mcp-server \
  --traffic v2=100 \
  -n netapp-mcp
```

## Configuration

### Environment Variables

Create a configuration file with your environment settings:

```bash
# .env file
# NetApp ActiveIQ Configuration
NETAPP_UM_HOST=unified-manager.company.com
NETAPP_USERNAME=serviceaccount
NETAPP_PASSWORD=secure-password
NETAPP_VERIFY_SSL=false

# MCP Server Configuration
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
MCP_LOG_LEVEL=INFO

# Optional: Advanced Settings
MCP_TIMEOUT=30
MCP_MAX_CONNECTIONS=100
MCP_CACHE_TTL=300

# Optional: Temporal Integration
TEMPORAL_HOST=temporal-server:7233
TEMPORAL_NAMESPACE=netapp-workflows
TEMPORAL_TASK_QUEUE=netapp-tasks

# Optional: Prometheus Metrics
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Optional: Authentication
AUTH_ENABLED=false
AUTH_SECRET_KEY=your-secret-key
AUTH_ALGORITHM=HS256
```

### Configuration File

Alternatively, use a YAML configuration file:

```yaml
# config.yaml
netapp:
  um_host: "unified-manager.company.com"
  username: "serviceaccount"
  password: "secure-password"
  verify_ssl: false
  timeout: 30

server:
  host: "0.0.0.0"
  port: 8080
  log_level: "INFO"
  max_connections: 100

cache:
  enabled: true
  ttl: 300
  redis_url: "redis://localhost:6379"

temporal:
  enabled: false
  host: "localhost:7233"
  namespace: "default"
  task_queue: "netapp-tasks"

monitoring:
  prometheus:
    enabled: true
    port: 9090
    path: "/metrics"

security:
  auth_enabled: false
  secret_key: "your-secret-key"
  ssl_cert: "/path/to/cert.pem"
  ssl_key: "/path/to/key.pem"
```

## Running the Server

### Docker Deployment

#### Basic Docker Run

```bash
docker run -d \
  --name netapp-mcp-server \
  --env-file .env \
  -p 8080:8080 \
  netapp/activeiq-mcp-server:latest
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  netapp-mcp-server:
    image: netapp/activeiq-mcp-server:latest
    container_name: netapp-mcp-server
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "9090:9090"  # Prometheus metrics
    env_file:
      - .env
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    container_name: netapp-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Optional: Temporal server
  temporal:
    image: temporalio/auto-setup:latest
    container_name: netapp-temporal
    restart: unless-stopped
    ports:
      - "7233:7233"
      - "8088:8080"  # Temporal Web UI
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=temporal
      - POSTGRES_PWD=temporal
      - POSTGRES_SEEDS=postgres

volumes:
  redis_data:
```

### Python Deployment

#### Direct Execution

```bash
# Using environment variables
export NETAPP_UM_HOST=your-um-host.company.com
export NETAPP_USERNAME=admin
export NETAPP_PASSWORD=your-password

# Run the server
python -m netapp_mcp_server

# Or with config file
python -m netapp_mcp_server --config config.yaml
```

#### Using systemd (Linux)

```ini
# /etc/systemd/system/netapp-mcp-server.service
[Unit]
Description=NetApp ActiveIQ MCP Server
After=network.target

[Service]
Type=simple
User=netapp
Group=netapp
WorkingDirectory=/opt/netapp-mcp-server
Environment=PATH=/opt/netapp-mcp-server/venv/bin
EnvironmentFile=/opt/netapp-mcp-server/.env
ExecStart=/opt/netapp-mcp-server/venv/bin/python -m netapp_mcp_server
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable netapp-mcp-server
sudo systemctl start netapp-mcp-server
sudo systemctl status netapp-mcp-server
```

## Verification

### Health Check

```bash
# Check server health
curl http://localhost:8080/health

# Expected response:
{
  "status": "healthy",
  "version": "1.2.0",
  "netapp_connection": "ok",
  "uptime": "2h 15m 30s"
}
```

### MCP Tools Test

```bash
# List available tools
curl http://localhost:8080/tools

# Test a simple tool
curl -X POST http://localhost:8080/tools/get_clusters \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}'
```

### Connection Test

```bash
# Test NetApp connection
curl -X POST http://localhost:8080/tools/test_connection \
  -H "Content-Type: application/json"
```

## Troubleshooting

### Common Issues

#### Cannot Connect to NetApp Unified Manager

```bash
# Test network connectivity
curl -k https://your-um-host.company.com/api/v2/datacenter/cluster/clusters

# Check DNS resolution
nslookup your-um-host.company.com

# Test with explicit credentials
curl -k -u "username:password" https://your-um-host.company.com/api/v2/datacenter/cluster/clusters
```

#### Server Won't Start

```bash
# Check logs (Docker)
docker logs netapp-mcp-server

# Check logs (Python)
tail -f logs/netapp-mcp-server.log

# Check configuration
python -m netapp_mcp_server --validate-config
```

#### Permission Issues

```bash
# Check file permissions
ls -la config.yaml .env

# Fix permissions
chmod 600 .env config.yaml
```

### Log Locations

- **Docker**: `docker logs netapp-mcp-server`
- **Python**: `./logs/netapp-mcp-server.log`
- **systemd**: `journalctl -u netapp-mcp-server`

## Security Considerations

### Credential Management

- Store credentials in secure environment variables or files
- Use dedicated service accounts with minimal required permissions
- Rotate passwords regularly
- Consider using secret management solutions (HashiCorp Vault, Kubernetes Secrets)

### Network Security

- Use HTTPS for all NetApp API communications
- Implement proper firewall rules
- Consider VPN or private network access
- Enable SSL/TLS for the MCP server

### Access Control

- Implement authentication for the MCP server
- Use role-based access control
- Monitor and audit access logs
- Implement rate limiting

## Next Steps

After successful installation:

1. **[Configure the Server](configuration.md)** - Detailed configuration options
2. **[Explore Architecture](../architecture/system-design.md)** - Understand the system design
3. **[Try Examples](../examples/basic-usage.md)** - Start with basic examples
4. **[Deploy to Production](../deployment/docker.md)** - Production deployment guide
