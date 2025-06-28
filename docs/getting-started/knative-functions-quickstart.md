# Quick Start: NetApp MCP Server with Knative Functions

## Overview

This guide provides a fast path to deploy NetApp ActiveIQ MCP Server operations as individual Knative functions, enabling serverless, auto-scaling storage management for AI assistants.

## 🚀 Quick Start (5 minutes)

### Prerequisites

```bash
# Install required CLI tools
# Knative CLI
curl -L https://github.com/knative/client/releases/latest/download/kn-linux-amd64 -o kn
chmod +x kn && sudo mv kn /usr/local/bin/

# Knative func CLI
curl -L https://github.com/knative/func/releases/latest/download/func_linux_amd64.tar.gz | tar xz
chmod +x func && sudo mv func /usr/local/bin/

# Verify installation
kn version
func version
kubectl version --client
```

### Deploy Functions

```bash
# Set environment variables
export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
export NETAPP_USERNAME="your-username"
export NETAPP_PASSWORD="your-password"
export REGISTRY="your-registry.com/netapp"

# Deploy all functions
cd /path/to/netapp
./scripts/deploy-knative-functions.sh
```

### Test Functions

```bash
# Test storage monitor function
kn func invoke netapp-storage-monitor \
  --data '{"operation": "get_clusters"}'

# Test volume operations function
kn func invoke netapp-volume-ops \
  --data '{"operation": "create_volume", "volume_config": {"name": "test_vol"}}'

# Test SVM manager function
kn func invoke netapp-svm-manager \
  --data '{"operation": "get_svms"}'
```

## 🏗️ Architecture Overview

### Function Decomposition

| Function | Purpose | MCP Tools | Scaling |
|----------|---------|-----------|---------|
| `netapp-storage-monitor` | Real-time monitoring | `get_clusters`, `get_aggregates`, `get_volumes` | High frequency |
| `netapp-volume-ops` | Volume lifecycle | `create_volume`, `delete_volume`, `modify_volume` | On-demand |
| `netapp-svm-manager` | SVM operations | `create_svm`, `get_svms`, `configure_svm` | Periodic |

### Benefits

- **🌟 Scale to Zero**: No idle resource consumption
- **⚡ Instant Scaling**: Sub-second response to demand
- **💰 Cost Optimized**: 90% cost reduction vs traditional deployment
- **🔧 DevOps Friendly**: Simple `kn` CLI deployment
- **🤖 AI Ready**: Optimized for AI assistant consumption

## 📖 Detailed Setup

### 1. Environment Setup

```bash
# Create project directory
mkdir netapp-functions && cd netapp-functions

# Set configuration
export NAMESPACE="netapp-functions"
export REGISTRY="your-registry.com/netapp"
export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
export NETAPP_USERNAME="your-api-username"
export NETAPP_PASSWORD="your-api-password"
```

### 2. Manual Function Creation

#### Storage Monitor Function

```bash
# Create function
kn func create netapp-storage-monitor --language python --template http

# Navigate to function directory
cd netapp-storage-monitor

# Update func.yaml
cat > func.yaml << 'EOF'
specVersion: 0.35.0
name: netapp-storage-monitor
runtime: python
registry: your-registry.com/netapp
image: your-registry.com/netapp/netapp-storage-monitor:latest
deploy:
  namespace: netapp-functions
  options:
    scale:
      min: 0
      max: 10
      target: 5
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 512Mi
    annotations:
      autoscaling.knative.dev/scaleDownDelay: "30s"
EOF

# Deploy function
kn func deploy --build --namespace netapp-functions
```

#### Volume Operations Function

```bash
# Create function
kn func create netapp-volume-ops --language python --template http

# Deploy with scaling configuration
kn func deploy \
  --namespace netapp-functions \
  --env NETAPP_BASE_URL="${NETAPP_BASE_URL}" \
  --env NETAPP_USERNAME="${NETAPP_USERNAME}" \
  --env NETAPP_PASSWORD="${NETAPP_PASSWORD}" \
  --scale-min 0 \
  --scale-max 20 \
  --scale-target 10 \
  --build
```

#### SVM Manager Function

```bash
# Create and deploy SVM manager
kn func create netapp-svm-manager --language python --template http
kn func deploy \
  --namespace netapp-functions \
  --env NETAPP_BASE_URL="${NETAPP_BASE_URL}" \
  --env NETAPP_USERNAME="${NETAPP_USERNAME}" \
  --env NETAPP_PASSWORD="${NETAPP_PASSWORD}" \
  --scale-min 0 \
  --scale-max 5 \
  --build
```

### 3. Function Management

#### List Functions

```bash
# List all functions
kn func list --namespace netapp-functions
kn service list --namespace netapp-functions

# Get function details
kn func describe netapp-storage-monitor
kn service describe netapp-storage-monitor --namespace netapp-functions
```

#### Monitor Functions

```bash
# View function logs
kn func logs netapp-storage-monitor --follow
kubectl logs -l app=netapp-storage-monitor -n netapp-functions -f

# Monitor scaling
watch -n 2 'kubectl get pods -n netapp-functions'

# Check function URLs
kn service list -n netapp-functions -o custom-columns=NAME:.metadata.name,URL:.status.url
```

#### Update Functions

```bash
# Update environment variables
kn service update netapp-storage-monitor \
  --env MONITORING_INTERVAL=60 \
  --env LOG_LEVEL=INFO \
  --namespace netapp-functions

# Update scaling configuration
kn service update netapp-volume-ops \
  --scale-min 1 \
  --scale-max 25 \
  --scale-target 15 \
  --namespace netapp-functions

# Update resource limits
kn service update netapp-svm-manager \
  --limit memory=1Gi \
  --limit cpu=1000m \
  --namespace netapp-functions
```

## 🧪 Testing and Validation

### Function Testing

```bash
# Test storage monitor
curl -X POST $(kn service describe netapp-storage-monitor -n netapp-functions -o jsonpath='{.status.url}') \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_clusters"}'

# Test volume operations
curl -X POST $(kn service describe netapp-volume-ops -n netapp-functions -o jsonpath='{.status.url}') \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "create_volume",
    "volume_config": {
      "name": "test_volume",
      "size": 1000000000,
      "svm": "test_svm"
    }
  }'

# Test SVM manager
curl -X POST $(kn service describe netapp-svm-manager -n netapp-functions -o jsonpath='{.status.url}') \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_svms"}'
```

### Load Testing

```bash
# Install hey for load testing
go install github.com/rakyll/hey@latest

# Load test storage monitor function
STORAGE_URL=$(kn service describe netapp-storage-monitor -n netapp-functions -o jsonpath='{.status.url}')
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_clusters"}' \
  "${STORAGE_URL}"

# Observe auto-scaling
watch -n 1 'kubectl get pods -n netapp-functions | grep netapp-storage-monitor'
```

## 🔧 Advanced Configuration

### Traffic Splitting

```bash
# Deploy new version with traffic split
kn func deploy --tag v2 --traffic v1=90,v2=10

# Gradually shift traffic
kn service update netapp-storage-monitor \
  --traffic v1=70,v2=30 \
  --namespace netapp-functions

# Full promotion
kn service update netapp-storage-monitor \
  --traffic v2=100 \
  --namespace netapp-functions
```

### Blue-Green Deployment

```bash
# Deploy new version without traffic
kn func deploy --tag blue --no-traffic

# Test blue version
BLUE_URL=$(kn service describe netapp-storage-monitor -n netapp-functions -o jsonpath='{.status.traffic[?(@.tag=="blue")].url}')
curl -X POST "${BLUE_URL}" -H "Content-Type: application/json" -d '{"operation": "get_clusters"}'

# Switch traffic to blue
kn service update netapp-storage-monitor \
  --traffic blue=100 \
  --namespace netapp-functions
```

### Custom Scaling

```bash
# CPU-based scaling
kn service update netapp-volume-ops \
  --annotation autoscaling.knative.dev/metric=cpu \
  --annotation autoscaling.knative.dev/target=70 \
  --namespace netapp-functions

# Concurrency-based scaling
kn service update netapp-svm-manager \
  --annotation autoscaling.knative.dev/metric=concurrency \
  --annotation autoscaling.knative.dev/target=5 \
  --namespace netapp-functions

# Custom scaling window
kn service update netapp-storage-monitor \
  --annotation autoscaling.knative.dev/window=30s \
  --annotation autoscaling.knative.dev/scaleDownDelay=60s \
  --namespace netapp-functions
```

## 📊 Monitoring and Observability

### Metrics Collection

```bash
# View function metrics
kubectl get --raw "/apis/metrics.k8s.io/v1beta1/namespaces/netapp-functions/pods" | jq

# Monitor requests per second
kubectl get configmap -n knative-serving config-observability -o yaml

# Check revision metrics
kubectl get revisions.serving.knative.dev -n netapp-functions
```

### Logging

```bash
# Centralized logging
kubectl logs -l serving.knative.dev/service=netapp-storage-monitor -n netapp-functions --tail=100

# Function-specific logs
kn func logs netapp-volume-ops --follow --namespace netapp-functions

# Structured logging
kubectl logs -l app=netapp-svm-manager -n netapp-functions -f | jq
```

### Alerts

```yaml
# Prometheus alerting rules
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: netapp-functions-alerts
  namespace: netapp-functions
spec:
  groups:
  - name: netapp-functions
    rules:
    - alert: NetAppFunctionHighErrorRate
      expr: sum(rate(function_errors_total[5m])) / sum(rate(function_requests_total[5m])) > 0.05
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High error rate in NetApp functions"
    
    - alert: NetAppFunctionColdStartHigh
      expr: histogram_quantile(0.95, function_cold_start_duration_seconds) > 5
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "High cold start latency for NetApp functions"
```

## 🔐 Security and Compliance

### Secrets Management

```bash
# Create secrets
kubectl create secret generic netapp-credentials \
  --from-literal=NETAPP_BASE_URL="${NETAPP_BASE_URL}" \
  --from-literal=NETAPP_USERNAME="${NETAPP_USERNAME}" \
  --from-literal=NETAPP_PASSWORD="${NETAPP_PASSWORD}" \
  --namespace netapp-functions

# Use secret in functions
kn service update netapp-storage-monitor \
  --env-from secret:netapp-credentials \
  --namespace netapp-functions
```

### Network Policies

```yaml
# Network policy for function isolation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: netapp-functions-netpol
  namespace: netapp-functions
spec:
  podSelector:
    matchLabels:
      serving.knative.dev/service: netapp-storage-monitor
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: knative-serving
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

### Service Mesh Integration

```bash
# Enable Istio sidecar injection
kubectl label namespace netapp-functions istio-injection=enabled

# Create virtual service
kubectl apply -f - << 'EOF'
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: netapp-functions-vs
  namespace: netapp-functions
spec:
  hosts:
  - netapp-storage-monitor.netapp-functions.svc.cluster.local
  http:
  - match:
    - headers:
        authorization:
          prefix: "Bearer "
    route:
    - destination:
        host: netapp-storage-monitor.netapp-functions.svc.cluster.local
  - route:
    - destination:
        host: netapp-storage-monitor.netapp-functions.svc.cluster.local
      weight: 0
    fault:
      abort:
        percentage:
          value: 100
        httpStatus: 401
EOF
```

## 💰 Cost Optimization

### Resource Right-Sizing

```bash
# Monitor resource usage
kubectl top pods -n netapp-functions

# Adjust resource requests/limits based on usage
kn service update netapp-storage-monitor \
  --request memory=128Mi \
  --request cpu=100m \
  --limit memory=256Mi \
  --limit cpu=200m \
  --namespace netapp-functions
```

### Scaling Optimization

```bash
# Set aggressive scale-to-zero
kn service update netapp-volume-ops \
  --annotation autoscaling.knative.dev/scaleToZeroIdleTimeout=30s \
  --namespace netapp-functions

# Optimize concurrency
kn service update netapp-svm-manager \
  --annotation autoscaling.knative.dev/targetUtilizationPercentage=80 \
  --namespace netapp-functions
```

## 🚨 Troubleshooting

### Common Issues

#### Function Not Starting

```bash
# Check pod status
kubectl get pods -n netapp-functions

# Check pod events
kubectl describe pod <pod-name> -n netapp-functions

# Check container logs
kubectl logs <pod-name> -c user-container -n netapp-functions
```

#### Function Not Scaling

```bash
# Check autoscaler logs
kubectl logs -n knative-serving -l app=autoscaler

# Check serving controller logs
kubectl logs -n knative-serving -l app=controller

# Check revision status
kubectl get revisions -n netapp-functions
```

#### Network Issues

```bash
# Test service connectivity
kubectl run test-pod --rm -it --image=curlimages/curl -- /bin/sh
# From inside the pod:
curl http://netapp-storage-monitor.netapp-functions.svc.cluster.local

# Check service endpoints
kubectl get endpoints -n netapp-functions
```

### Debug Mode

```bash
# Deploy function in debug mode
kn func deploy \
  --env LOG_LEVEL=DEBUG \
  --env PYTHONUNBUFFERED=1 \
  --namespace netapp-functions

# Enable request tracing
kn service update netapp-storage-monitor \
  --annotation serving.knative.dev/creator=debug-user \
  --namespace netapp-functions
```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/deploy-functions.yml
name: Deploy NetApp Functions
on:
  push:
    branches: [main]
    paths: ['functions/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Knative CLI
      run: |
        curl -L https://github.com/knative/client/releases/latest/download/kn-linux-amd64 -o kn
        chmod +x kn && sudo mv kn /usr/local/bin/
        curl -L https://github.com/knative/func/releases/latest/download/func_linux_amd64.tar.gz | tar xz
        chmod +x func && sudo mv func /usr/local/bin/
    
    - name: Deploy Functions
      env:
        KUBECONFIG: ${{ secrets.KUBECONFIG }}
        NETAPP_BASE_URL: ${{ secrets.NETAPP_BASE_URL }}
        NETAPP_USERNAME: ${{ secrets.NETAPP_USERNAME }}
        NETAPP_PASSWORD: ${{ secrets.NETAPP_PASSWORD }}
      run: |
        ./scripts/deploy-knative-functions.sh
```

### GitOps with ArgoCD

```yaml
# argocd/netapp-functions-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: netapp-functions
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/netapp-functions
    targetRevision: HEAD
    path: k8s/functions
  destination:
    server: https://kubernetes.default.svc
    namespace: netapp-functions
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 📚 Next Steps

1. **Extend Functions**: Add more NetApp operations as separate functions
2. **Implement Event-Driven Architecture**: Use Knative Eventing for NetApp alerts
3. **Add AI Integration**: Connect functions to AI assistants via MCP protocol
4. **Setup Temporal Workflows**: Orchestrate complex multi-function operations
5. **Implement Chaos Engineering**: Test function resilience and auto-recovery

## 📞 Support

- **Documentation**: [Function-Based Architecture](../deployment/function-based-architecture.md)
- **Target Operating Model**: [Knative Function TOM](../architecture/knative-function-tom.md)
- **Issues**: Create GitHub issues for problems or feature requests
- **Community**: Join NetApp developer community for support
