# NetApp MCP Server - Knative Functions Deployment Guide

Complete guide for deploying the NetApp ActiveIQ MCP Server as Knative Functions using the `kn func` CLI for serverless, auto-scaling operation.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Setup](#installation-setup)
4. [Complete MCP Server Deployment](#complete-mcp-server-deployment)
5. [Individual Function Components](#individual-function-components)
6. [Testing and Validation](#testing-and-validation)
7. [Management Operations](#management-operations)
8. [Traffic Management](#traffic-management)
9. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
10. [Production Considerations](#production-considerations)

## Overview

This deployment method transforms the NetApp MCP Server into serverless Knative Functions that:

- **Scale to Zero**: No resource consumption when idle
- **Auto-scale**: Instant scaling based on demand
- **Cost Optimized**: Pay only for actual usage
- **High Availability**: Built-in redundancy and failover
- **Blue-Green Deployments**: Zero-downtime updates

### Architecture Benefits

```
┌─────────────────────────────────────────────────────┐
│                 AI Assistant                        │
└─────────────────┬───────────────────────────────────┘
                  │ MCP Protocol
                  │
┌─────────────────▼───────────────────────────────────┐
│              Knative Gateway                        │
│              (Istio/Kourier)                        │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│         NetApp MCP Server Function                  │
│    ┌─────────────────────────────────────────┐      │
│    │      Auto-scaling Pod                   │      │
│    │  ┌─────────────────────────────────┐    │      │
│    │  │     MCP Server Container        │    │      │
│    │  │   - FastMCP Framework          │    │      │
│    │  │   - NetApp API Client          │    │      │
│    │  │   - 17 MCP Tools               │    │      │
│    │  └─────────────────────────────────┘    │      │
│    └─────────────────────────────────────────┘      │
└─────────────────┬───────────────────────────────────┘
                  │ HTTPS API Calls
                  │
┌─────────────────▼───────────────────────────────────┐
│         NetApp ActiveIQ Unified Manager             │
│              (External System)                      │
└─────────────────────────────────────────────────────┘
```

## Prerequisites

### Infrastructure Requirements

- **Kubernetes Cluster**: v1.24+ with Knative Serving installed
- **Knative Serving**: v1.8+ with networking layer (Istio/Kourier)
- **Container Registry**: Docker Hub, GCR, ECR, or private registry access
- **Resource Requirements**: 
  - Minimum: 2 vCPUs, 4GB RAM per cluster
  - Recommended: 4 vCPUs, 8GB RAM per cluster

### Access Requirements

- **Kubernetes Cluster**: Admin or sufficient RBAC permissions
- **NetApp ActiveIQ**: API access credentials
- **Container Registry**: Push/pull permissions

### Software Dependencies

- `kubectl` >= 1.24
- `docker` >= 20.10 (for building images)
- Access to NetApp ActiveIQ Unified Manager

## Installation Setup

### Step 1: Install Knative CLI Tools

```bash
# Install Knative CLI
curl -L https://github.com/knative/client/releases/latest/download/kn-darwin-amd64 -o kn
chmod +x kn && sudo mv kn /usr/local/bin/

# Install Knative func CLI
curl -L https://github.com/knative/func/releases/latest/download/func_darwin_amd64.tar.gz | tar xz
chmod +x func && sudo mv func /usr/local/bin/

# Verify installation
kn version
func version
kubectl version --client
```

### Step 2: Verify Knative Installation

```bash
# Check Knative Serving components
kubectl get pods -n knative-serving

# Verify networking layer
kubectl get pods -n kourier-system || kubectl get pods -n istio-system

# Check custom resource definitions
kubectl get crd | grep knative
```

### Step 3: Prepare Environment Variables

```bash
# Set deployment configuration
export REGISTRY="your-registry.com/netapp"
export NAMESPACE="netapp-mcp"
export IMAGE_TAG="latest"

# NetApp ActiveIQ Configuration
export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
export NETAPP_USERNAME="your-username"
export NETAPP_PASSWORD="your-password"
export NETAPP_VERIFY_SSL="false"

# MCP Server Configuration
export MCP_SERVER_PORT="8080"
export MCP_LOG_LEVEL="INFO"

# Optional: Advanced Settings
export MCP_TIMEOUT="30"
export MCP_MAX_CONNECTIONS="100"
export MCP_CACHE_TTL="300"
```

## Deployment Methods Overview

### Comparison: Knative Function CLI vs Manual YAML vs Source-to-URL

| Method | Build & Deploy Command | Source Format | Registry Needed | Example Use Case |
|--------|------------------------|---------------|-----------------|------------------|
| **Knative Functions CLI** | `kn func deploy --registry <registry>` | Local project | Yes | Quick local development |
| **Manual YAML** | `kubectl apply -f <manifest>.yaml` | Container image | Yes | Custom configuration |
| **Source-to-URL (Kaniko/Ko)** | `kubectl apply -f <manifest>.yaml` (with build spec) | Git repo (source) | Yes | CI/CD pipelines, Go apps |
| **Direct MCP Server** | `npx -y @modelcontextprotocol/server-filesystem /data` | Container args | Yes | Standard MCP servers |

### Key Benefits of kn func Approach

- **Streamlined Development**: `kn func deploy` for one-command deployment from local code
- **Automatic Container Building**: Built-in Buildpacks support for Python, Node.js, Go
- **Function Templates**: Pre-configured templates for HTTP, CloudEvents
- **Integrated Testing**: Built-in function invoke capabilities
- **Auto-scaling**: Knative provides concurrency controls and scale-to-zero out of the box
- **Blue-Green Deployments**: Native traffic splitting and rollback capabilities

## Complete MCP Server Deployment

### Step 1: Create Function Structure

```bash
# Method 1: Create function using kn func CLI (Recommended)
kn func create netapp-mcp-server --language python --template http
cd netapp-mcp-server

# Method 2: Create in existing directory
mkdir netapp-mcp-server && cd netapp-mcp-server
func create . --language python --template http
```

### Step 2: Configure Function Specification

Create `func.yaml`:

```yaml
specVersion: 0.35.0
name: netapp-mcp-server
runtime: python
registry: your-registry.com/netapp
image: your-registry.com/netapp/netapp-mcp-server:latest
created: 2025-06-28T14:00:00Z
invoke: gunicorn
build:
  builder: pack
  buildpacks: 
    - gcr.io/paketo-buildpacks/python
  env:
    - name: BP_PIP_VERSION
      value: "latest"
run:
  env:
    - name: FUNCTION_TARGET
      value: main
    - name: PYTHONUNBUFFERED
      value: "1"
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
      serving.knative.dev/timeout-seconds: "300"
```

### Step 3: Prepare Dependencies

Create `requirements.txt`:

```txt
fastmcp>=0.5.0
httpx>=0.25.0
pydantic>=2.0.0
python-dotenv>=1.0.0
uvicorn>=0.24.0
parliament-functions>=1.0.0
aiofiles>=23.0.0
asyncio-mqtt>=0.13.0
```

### Step 4: Copy MCP Server Code

```bash
# Copy the main MCP server implementation
cp ../mcp_server.py func.py

# Ensure the main function is compatible with Knative Functions
# The func.py should have a main() function that handles HTTP requests
```

### Step 5: Adapt MCP Server for Functions

Create a function-compatible wrapper in `func.py`:

```python
import asyncio
import json
import os
from datetime import datetime
from parliament import Context
from typing import Dict, Any

# Import your existing MCP server components
try:
    from mcp_server import (
        get_clusters, get_aggregates, get_volumes, create_volume,
        delete_volume, modify_volume, create_svm, get_svms,
        configure_svm, test_connection
    )
except ImportError:
    # Fallback implementations for testing
    async def get_clusters(**kwargs):
        return {"records": [], "num_records": 0}
    
    async def test_connection(**kwargs):
        return {"status": "connected", "timestamp": datetime.utcnow().isoformat()}

# Function entry point
async def main(context: Context) -> Dict[str, Any]:
    """
    NetApp MCP Server Function main entry point
    Handles HTTP requests and routes them to appropriate MCP tools
    """
    try:
        # Parse request
        if hasattr(context.request, 'json') and context.request.json:
            request_data = context.request.json
        else:
            # Handle GET requests with query parameters
            request_data = dict(context.request.query_params) if hasattr(context.request, 'query_params') else {}
        
        # Extract operation and arguments
        operation = request_data.get('operation', 'health_check')
        arguments = request_data.get('arguments', {})
        
        # Route to appropriate MCP tool
        result = await route_operation(operation, arguments)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'operation': operation,
                'timestamp': datetime.utcnow().isoformat(),
                'function_name': os.getenv('K_SERVICE', 'netapp-mcp-server'),
                'result': result
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'operation': request_data.get('operation', 'unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'function_name': os.getenv('K_SERVICE', 'netapp-mcp-server')
            })
        }

async def route_operation(operation: str, arguments: Dict[str, Any]) -> Any:
    """Route operations to appropriate MCP tools"""
    
    # Health check
    if operation == 'health_check':
        return await test_connection()
    
    # Cluster operations
    elif operation == 'get_clusters':
        return await get_clusters(**arguments)
    
    # Aggregate operations
    elif operation == 'get_aggregates':
        return await get_aggregates(**arguments)
    
    # Volume operations
    elif operation == 'get_volumes':
        return await get_volumes(**arguments)
    elif operation == 'create_volume':
        return await create_volume(**arguments)
    elif operation == 'delete_volume':
        return await delete_volume(**arguments)
    elif operation == 'modify_volume':
        return await modify_volume(**arguments)
    
    # SVM operations
    elif operation == 'get_svms':
        return await get_svms(**arguments)
    elif operation == 'create_svm':
        return await create_svm(**arguments)
    elif operation == 'configure_svm':
        return await configure_svm(**arguments)
    
    # Connection test
    elif operation == 'test_connection':
        return await test_connection(**arguments)
    
    else:
        raise ValueError(f"Unknown operation: {operation}")
```

### Step 6: Deploy the Function

```bash
# Create namespace if it doesn't exist
kubectl create namespace netapp-mcp --dry-run=client -o yaml | kubectl apply -f -

# Deploy function with all environment variables
func deploy \
  --namespace netapp-mcp \
  --env NETAPP_BASE_URL="${NETAPP_BASE_URL}" \
  --env NETAPP_USERNAME="${NETAPP_USERNAME}" \
  --env NETAPP_PASSWORD="${NETAPP_PASSWORD}" \
  --env NETAPP_VERIFY_SSL="${NETAPP_VERIFY_SSL}" \
  --env MCP_SERVER_PORT="${MCP_SERVER_PORT}" \
  --env MCP_LOG_LEVEL="${MCP_LOG_LEVEL}" \
  --env MCP_TIMEOUT="${MCP_TIMEOUT}" \
  --env MCP_MAX_CONNECTIONS="${MCP_MAX_CONNECTIONS}" \
  --env MCP_CACHE_TTL="${MCP_CACHE_TTL}" \
  --build \
  --verbose
```

## Individual Function Components

### Deploy Using Existing Script

```bash
# Use the provided script for individual function deployment
cd /Users/brun_s/Documents/veille-technologique/Professionel/donnees-d-entree/PE-AsProduct/netapp

# Set environment variables
export NAMESPACE="netapp-functions"
export REGISTRY="${REGISTRY}"
export NETAPP_BASE_URL="${NETAPP_BASE_URL}"
export NETAPP_USERNAME="${NETAPP_USERNAME}"
export NETAPP_PASSWORD="${NETAPP_PASSWORD}"

# Deploy individual functions
./scripts/deploy-knative-functions.sh
```

## Testing and Validation

### Step 1: Verify Deployment

```bash
# Check function status
kn service list -n netapp-mcp

# Get function details
kn service describe netapp-mcp-server -n netapp-mcp

# Check pods
kubectl get pods -n netapp-mcp

# View function logs
kn func logs netapp-mcp-server --follow
```

### Step 2: Get Function URL

```bash
# Get the function URL
MCP_URL=$(kn service describe netapp-mcp-server -n netapp-mcp -o jsonpath='{.status.url}')
echo "MCP Server URL: $MCP_URL"

# Store for testing
export MCP_FUNCTION_URL="$MCP_URL"
```

### Step 3: Basic Health Check

```bash
# Test health endpoint
curl -X POST "$MCP_FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "health_check"
  }'

# Expected response:
# {
#   "success": true,
#   "operation": "health_check",
#   "timestamp": "2025-06-28T14:00:00Z",
#   "function_name": "netapp-mcp-server",
#   "result": {
#     "status": "connected",
#     "timestamp": "2025-06-28T14:00:00Z"
#   }
# }
```

### Step 4: Test MCP Operations

```bash
# Test cluster information
curl -X POST "$MCP_FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "get_clusters",
    "arguments": {}
  }'

# Test volume operations
curl -X POST "$MCP_FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "get_volumes",
    "arguments": {
      "fields": "name,size,state"
    }
  }'

# Test SVM operations
curl -X POST "$MCP_FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "get_svms",
    "arguments": {}
  }'
```

### Step 5: Load Testing

```bash
# Install hey for load testing (if not installed)
# brew install hey  # macOS
# go install github.com/rakyll/hey@latest  # Go

# Perform load test
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_clusters", "arguments": {}}' \
  "$MCP_FUNCTION_URL"

# Monitor scaling during load test
watch -n 1 'kubectl get pods -n netapp-mcp'
```

## Management Operations

### Update Function Configuration

```bash
# Update environment variables
kn service update netapp-mcp-server \
  --env MCP_LOG_LEVEL=DEBUG \
  --env MCP_TIMEOUT=60 \
  -n netapp-mcp

# Update scaling configuration
kn service update netapp-mcp-server \
  --scale-min 1 \
  --scale-max 20 \
  --scale-target 50 \
  -n netapp-mcp

# Update resource limits
kn service update netapp-mcp-server \
  --limit memory=2Gi \
  --limit cpu=2000m \
  --request memory=1Gi \
  --request cpu=1000m \
  -n netapp-mcp
```

### Function Information

```bash
# Get function URL
kn service describe netapp-mcp-server -n netapp-mcp -o jsonpath='{.status.url}'

# Get function configuration
kn service describe netapp-mcp-server -n netapp-mcp -o yaml

# List all revisions
kn revision list -s netapp-mcp-server -n netapp-mcp

# Get revision details
kn revision describe netapp-mcp-server-<revision> -n netapp-mcp
```

## Traffic Management

### Blue-Green Deployment

```bash
# Deploy new version without traffic
func deploy --tag blue --no-traffic

# Test blue version
BLUE_URL=$(kn service describe netapp-mcp-server -n netapp-mcp -o jsonpath='{.status.traffic[?(@.tag=="blue")].url}')
curl -X POST "$BLUE_URL" -H "Content-Type: application/json" -d '{"operation": "health_check"}'

# Switch traffic to blue version
kn service update netapp-mcp-server \
  --traffic blue=100 \
  -n netapp-mcp
```

### Canary Deployment

```bash
# Split traffic between versions
kn service update netapp-mcp-server \
  --traffic v1=90,v2=10 \
  -n netapp-mcp

# Gradually shift traffic
kn service update netapp-mcp-server \
  --traffic v1=70,v2=30 \
  -n netapp-mcp

# Full promotion
kn service update netapp-mcp-server \
  --traffic v2=100 \
  -n netapp-mcp
```

### Rollback

```bash
# List revisions
kn revision list -s netapp-mcp-server -n netapp-mcp

# Rollback to previous revision
kn service update netapp-mcp-server \
  --traffic @latest=0,netapp-mcp-server-00001=100 \
  -n netapp-mcp
```

## Monitoring and Troubleshooting

### Monitoring

```bash
# View real-time logs
kubectl logs -f -l serving.knative.dev/service=netapp-mcp-server -n netapp-mcp

# Monitor function metrics
kubectl get --raw "/apis/metrics.k8s.io/v1beta1/namespaces/netapp-mcp/pods" | jq

# Check autoscaler logs
kubectl logs -n knative-serving -l app=autoscaler

# Monitor scaling events
kubectl get events -n netapp-mcp --sort-by='.lastTimestamp'
```

### Common Issues

#### Function Not Starting

```bash
# Check pod status
kubectl get pods -n netapp-mcp

# Describe pod for events
kubectl describe pod <pod-name> -n netapp-mcp

# Check container logs
kubectl logs <pod-name> -c user-container -n netapp-mcp
```

#### Function Not Scaling

```bash
# Check Knative serving controller logs
kubectl logs -n knative-serving -l app=controller

# Check autoscaler configuration
kubectl get configmap config-autoscaler -n knative-serving -o yaml

# Verify service configuration
kn service describe netapp-mcp-server -n netapp-mcp
```

#### Network Issues

```bash
# Test service from within cluster
kubectl run test-pod --rm -it --image=curlimages/curl -- /bin/sh
# From inside the pod:
curl http://netapp-mcp-server.netapp-mcp.svc.cluster.local

# Check service endpoints
kubectl get endpoints -n netapp-mcp

# Verify ingress/gateway configuration
kubectl get gateways,virtualservices -n netapp-mcp
```

### Debugging Mode

```bash
# Deploy function with debug settings
func deploy \
  --env LOG_LEVEL=DEBUG \
  --env PYTHONUNBUFFERED=1 \
  --env MCP_DEBUG=true \
  -n netapp-mcp

# Enable debug annotations
kn service update netapp-mcp-server \
  --annotation serving.knative.dev/creator=debug-user \
  -n netapp-mcp
```

## Production Considerations

### Security

```bash
# Create namespace with security labels
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: netapp-mcp
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
EOF

# Use secrets for credentials
kubectl create secret generic netapp-credentials \
  --from-literal=NETAPP_BASE_URL="$NETAPP_BASE_URL" \
  --from-literal=NETAPP_USERNAME="$NETAPP_USERNAME" \
  --from-literal=NETAPP_PASSWORD="$NETAPP_PASSWORD" \
  -n netapp-mcp

# Deploy with secret reference
kn service update netapp-mcp-server \
  --env-from secret:netapp-credentials \
  -n netapp-mcp
```

### Performance Optimization

```yaml
# Optimized func.yaml for production
deploy:
  options:
    scale:
      min: 2  # Keep minimum instances warm
      max: 50  # Allow higher scaling
      metric: rps  # Requests per second scaling
      target: 10
    resources:
      requests:
        cpu: 1000m
        memory: 1Gi
      limits:
        cpu: 4000m
        memory: 2Gi
    annotations:
      autoscaling.knative.dev/scaleDownDelay: "300s"
      autoscaling.knative.dev/window: "60s"
      autoscaling.knative.dev/targetUtilizationPercentage: "70"
      run.googleapis.com/cpu-throttling: "false"
```

### Monitoring Setup

```bash
# Install Prometheus ServiceMonitor
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: netapp-mcp-server
  namespace: netapp-mcp
spec:
  selector:
    matchLabels:
      serving.knative.dev/service: netapp-mcp-server
  endpoints:
  - port: http-userland
    path: /metrics
    interval: 30s
EOF
```

### Backup and Recovery

```bash
# Backup function configuration
kubectl get service.serving.knative.dev/netapp-mcp-server -n netapp-mcp -o yaml > netapp-mcp-server-backup.yaml

# Backup secrets
kubectl get secret netapp-credentials -n netapp-mcp -o yaml > netapp-credentials-backup.yaml

# Restore from backup
kubectl apply -f netapp-mcp-server-backup.yaml
kubectl apply -f netapp-credentials-backup.yaml
```

## Conclusion

This guide provides comprehensive instructions for deploying the NetApp MCP Server as Knative Functions. The serverless approach offers significant benefits in terms of cost optimization, scalability, and operational efficiency while maintaining full functionality of the MCP server.

For additional information, refer to:
- [Knative Functions Documentation](../getting-started/knative-functions-quickstart.md)
- [Architecture Overview](../architecture/knative-function-tom.md)
- [Troubleshooting Guide](../troubleshooting/common-issues.md)
