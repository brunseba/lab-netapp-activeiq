#!/bin/bash

# NetApp ActiveIQ MCP Server - Knative Function Deployment Script
# This script deploys NetApp MCP operations as individual Knative functions

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-netapp-functions}"
REGISTRY="${REGISTRY:-your-registry.com/netapp}"
BUILD_ARGS="${BUILD_ARGS:---build}"
VERBOSE="${VERBOSE:---verbose}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if kn CLI is installed
    if ! command -v kn &> /dev/null; then
        print_error "kn CLI is not installed. Please install Knative CLI first."
        exit 1
    fi
    
    # Check if func CLI is installed
    if ! command -v func &> /dev/null; then
        print_error "func CLI is not installed. Please install Knative func CLI first."
        exit 1
    fi
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if we can access the cluster
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot access Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# Function to create namespace if it doesn't exist
create_namespace() {
    print_status "Creating namespace ${NAMESPACE} if it doesn't exist..."
    
    if ! kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        kubectl create namespace "${NAMESPACE}"
        print_success "Namespace ${NAMESPACE} created"
    else
        print_warning "Namespace ${NAMESPACE} already exists"
    fi
}

# Function to create secrets
create_secrets() {
    print_status "Creating NetApp credentials secret..."
    
    # Check if required environment variables are set
    if [[ -z "${NETAPP_BASE_URL:-}" || -z "${NETAPP_USERNAME:-}" || -z "${NETAPP_PASSWORD:-}" ]]; then
        print_error "Required environment variables not set:"
        print_error "  NETAPP_BASE_URL - NetApp ActiveIQ API endpoint"
        print_error "  NETAPP_USERNAME - NetApp API username"
        print_error "  NETAPP_PASSWORD - NetApp API password"
        exit 1
    fi
    
    # Create or update secret
    kubectl create secret generic netapp-function-credentials \
        --namespace="${NAMESPACE}" \
        --from-literal=NETAPP_BASE_URL="${NETAPP_BASE_URL}" \
        --from-literal=NETAPP_USERNAME="${NETAPP_USERNAME}" \
        --from-literal=NETAPP_PASSWORD="${NETAPP_PASSWORD}" \
        --from-literal=NETAPP_VERIFY_SSL="false" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "NetApp credentials secret created/updated"
}

# Function to deploy a single function
deploy_function() {
    local func_name="$1"
    local func_description="$2"
    
    print_status "Deploying function: ${func_name}"
    
    # Create function directory if it doesn't exist
    if [[ ! -d "${func_name}" ]]; then
        print_status "Creating function ${func_name}..."
        func create "${func_name}" \
            --language python \
            --template http
    fi
    
    # Navigate to function directory
    pushd "${func_name}" > /dev/null
    
    # Update func.yaml with our configuration
    cat > func.yaml << EOF
specVersion: 0.35.0
name: ${func_name}
runtime: python
registry: ${REGISTRY}
image: ${REGISTRY}/${func_name}:latest
created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
invoke: gunicorn
build:
  builder: pack
  buildpacks: 
    - gcr.io/paketo-buildpacks/python
run:
  env:
    - name: FUNCTION_NAME
      value: '${func_name}'
    - name: FUNCTION_DESCRIPTION
      value: '${func_description}'
  envs:
    - name: FUNCTION_TARGET
      value: main
deploy:
  namespace: ${NAMESPACE}
  options:
    scale:
      min: 0
      max: 20
      metric: concurrency
      target: 10
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
      limits:
        cpu: 1000m
        memory: 512Mi
    annotations:
      autoscaling.knative.dev/scaleDownDelay: "30s"
      autoscaling.knative.dev/scaleUpDelay: "0s"
      description: "${func_description}"
EOF
    
    # Create requirements.txt if it doesn't exist
    if [[ ! -f requirements.txt ]]; then
        cat > requirements.txt << 'EOF'
fastmcp>=0.5.0
httpx>=0.25.0
pydantic>=2.0.0
python-dotenv>=1.0.0
uvicorn>=0.24.0
parliament-functions>=1.0.0
EOF
    fi
    
    # Deploy the function
    print_status "Deploying ${func_name} to cluster..."
    func deploy \
        --namespace="${NAMESPACE}" \
        --env-from secret:netapp-function-credentials \
        ${BUILD_ARGS} \
        ${VERBOSE}
    
    popd > /dev/null
    print_success "Function ${func_name} deployed successfully"
}

# Function to create storage monitor function
create_storage_monitor_function() {
    local func_name="netapp-storage-monitor"
    
    if [[ ! -d "${func_name}" ]]; then
        func create "${func_name}" --language python --template http
    fi
    
    # Create the function implementation
    cat > "${func_name}/func.py" << 'EOF'
import asyncio
import json
import os
from datetime import datetime
from parliament import Context

# Mock NetApp MCP tools - replace with actual implementation
async def get_clusters(**kwargs):
    """Get NetApp clusters information"""
    return {
        "records": [
            {
                "uuid": "cluster-001",
                "name": "production-cluster",
                "version": "9.13.1",
                "state": "up"
            }
        ],
        "num_records": 1
    }

async def get_aggregates(cluster_uuid=None, **kwargs):
    """Get aggregates information"""
    return {
        "records": [
            {
                "uuid": "aggr-001",
                "name": "aggr1",
                "cluster": {"uuid": cluster_uuid or "cluster-001"},
                "space": {"available": 1000000000, "used": 500000000}
            }
        ],
        "num_records": 1
    }

async def get_volumes(**kwargs):
    """Get volumes information"""
    return {
        "records": [
            {
                "uuid": "vol-001",
                "name": "vol1",
                "size": 100000000,
                "state": "online"
            }
        ],
        "num_records": 1
    }

async def main(context: Context):
    """Storage monitoring function main entry point"""
    try:
        # Parse request data
        if hasattr(context.request, 'json') and context.request.json:
            request_data = context.request.json
        else:
            # For GET requests, use query parameters
            request_data = dict(context.request.query_params) if hasattr(context.request, 'query_params') else {}
        
        operation = request_data.get('operation', 'get_clusters')
        
        # Route to appropriate operation
        if operation == 'get_clusters':
            result = await get_clusters()
        elif operation == 'get_aggregates':
            cluster_uuid = request_data.get('cluster_uuid')
            result = await get_aggregates(cluster_uuid=cluster_uuid)
        elif operation == 'get_volumes':
            filters = request_data.get('filters', {})
            result = await get_volumes(**filters)
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Unknown operation: {operation}'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'operation': operation,
                'timestamp': datetime.utcnow().isoformat(),
                'function_name': os.getenv('FUNCTION_NAME', 'netapp-storage-monitor'),
                'data': result
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'function_name': os.getenv('FUNCTION_NAME', 'netapp-storage-monitor')
            })
        }
EOF
}

# Function to create volume operations function
create_volume_ops_function() {
    local func_name="netapp-volume-ops"
    
    if [[ ! -d "${func_name}" ]]; then
        func create "${func_name}" --language python --template http
    fi
    
    # Create the function implementation
    cat > "${func_name}/func.py" << 'EOF'
import asyncio
import json
import os
from datetime import datetime
from parliament import Context

# Mock NetApp MCP tools - replace with actual implementation
async def create_volume(volume_config):
    """Create a new volume"""
    return {
        "uuid": "vol-new-001",
        "name": volume_config.get("name", "new_volume"),
        "size": volume_config.get("size", 1000000000),
        "svm": volume_config.get("svm", "default_svm"),
        "state": "online",
        "created": datetime.utcnow().isoformat()
    }

async def delete_volume(volume_uuid):
    """Delete a volume"""
    return {
        "uuid": volume_uuid,
        "deleted": True,
        "timestamp": datetime.utcnow().isoformat()
    }

async def modify_volume(volume_uuid, modifications):
    """Modify volume properties"""
    return {
        "uuid": volume_uuid,
        "modifications": modifications,
        "modified": True,
        "timestamp": datetime.utcnow().isoformat()
    }

async def main(context: Context):
    """Volume operations function main entry point"""
    try:
        # Parse request data
        if hasattr(context.request, 'json') and context.request.json:
            request_data = context.request.json
        else:
            request_data = {}
        
        operation = request_data.get('operation')
        
        if not operation:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Operation not specified'})
            }
        
        # Route to appropriate operation
        if operation == 'create_volume':
            volume_config = request_data.get('volume_config', {})
            result = await create_volume(volume_config)
        elif operation == 'delete_volume':
            volume_uuid = request_data.get('volume_uuid')
            if not volume_uuid:
                raise ValueError("volume_uuid is required for delete operation")
            result = await delete_volume(volume_uuid)
        elif operation == 'modify_volume':
            volume_uuid = request_data.get('volume_uuid')
            modifications = request_data.get('modifications', {})
            if not volume_uuid:
                raise ValueError("volume_uuid is required for modify operation")
            result = await modify_volume(volume_uuid, modifications)
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Unknown operation: {operation}'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'operation': operation,
                'timestamp': datetime.utcnow().isoformat(),
                'function_name': os.getenv('FUNCTION_NAME', 'netapp-volume-ops'),
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
                'function_name': os.getenv('FUNCTION_NAME', 'netapp-volume-ops')
            })
        }
EOF
}

# Function to create SVM manager function
create_svm_manager_function() {
    local func_name="netapp-svm-manager"
    
    if [[ ! -d "${func_name}" ]]; then
        func create "${func_name}" --language python --template http
    fi
    
    # Create the function implementation
    cat > "${func_name}/func.py" << 'EOF'
import asyncio
import json
import os
from datetime import datetime
from parliament import Context

# Mock NetApp MCP tools - replace with actual implementation
async def create_svm(svm_config):
    """Create a new Storage Virtual Machine"""
    return {
        "uuid": "svm-new-001",
        "name": svm_config.get("name", "new_svm"),
        "cluster": svm_config.get("cluster", "default_cluster"),
        "state": "running",
        "protocols": svm_config.get("protocols", ["nfs", "cifs"]),
        "created": datetime.utcnow().isoformat()
    }

async def get_svms(**kwargs):
    """Get SVM information"""
    return {
        "records": [
            {
                "uuid": "svm-001",
                "name": "production_svm",
                "state": "running",
                "protocols": ["nfs", "cifs"]
            }
        ],
        "num_records": 1
    }

async def configure_svm(svm_uuid, configuration):
    """Configure SVM settings"""
    return {
        "uuid": svm_uuid,
        "configuration": configuration,
        "configured": True,
        "timestamp": datetime.utcnow().isoformat()
    }

async def main(context: Context):
    """SVM manager function main entry point"""
    try:
        # Parse request data
        if hasattr(context.request, 'json') and context.request.json:
            request_data = context.request.json
        else:
            request_data = dict(context.request.query_params) if hasattr(context.request, 'query_params') else {}
        
        operation = request_data.get('operation', 'get_svms')
        
        # Route to appropriate operation
        if operation == 'get_svms':
            result = await get_svms()
        elif operation == 'create_svm':
            svm_config = request_data.get('svm_config', {})
            result = await create_svm(svm_config)
        elif operation == 'configure_svm':
            svm_uuid = request_data.get('svm_uuid')
            configuration = request_data.get('configuration', {})
            if not svm_uuid:
                raise ValueError("svm_uuid is required for configure operation")
            result = await configure_svm(svm_uuid, configuration)
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Unknown operation: {operation}'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'operation': operation,
                'timestamp': datetime.utcnow().isoformat(),
                'function_name': os.getenv('FUNCTION_NAME', 'netapp-svm-manager'),
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
                'function_name': os.getenv('FUNCTION_NAME', 'netapp-svm-manager')
            })
        }
EOF
}

# Function to test functions
test_functions() {
    print_status "Testing deployed functions..."
    
    local functions=("netapp-storage-monitor" "netapp-volume-ops" "netapp-svm-manager")
    
    for func_name in "${functions[@]}"; do
        print_status "Testing ${func_name}..."
        
        # Get function URL
        local func_url
        func_url=$(kn service describe "${func_name}" -n "${NAMESPACE}" -o jsonpath='{.status.url}' 2>/dev/null || echo "")
        
        if [[ -n "${func_url}" ]]; then
            # Test the function
            local test_data='{"operation": "test"}'
            if [[ "${func_name}" == "netapp-storage-monitor" ]]; then
                test_data='{"operation": "get_clusters"}'
            elif [[ "${func_name}" == "netapp-volume-ops" ]]; then
                test_data='{"operation": "create_volume", "volume_config": {"name": "test_vol", "size": 1000000000}}'
            elif [[ "${func_name}" == "netapp-svm-manager" ]]; then
                test_data='{"operation": "get_svms"}'
            fi
            
            local response
            response=$(curl -s -X POST "${func_url}" \
                -H "Content-Type: application/json" \
                -d "${test_data}" || echo "CURL_FAILED")
            
            if [[ "${response}" != "CURL_FAILED" ]]; then
                print_success "${func_name} is responding"
            else
                print_warning "${func_name} test failed - may still be starting"
            fi
        else
            print_warning "Could not get URL for ${func_name}"
        fi
    done
}

# Main deployment function
main() {
    print_status "Starting NetApp MCP Knative Functions deployment..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create namespace
    create_namespace
    
    # Create secrets
    create_secrets
    
    # Create function implementations
    print_status "Creating function implementations..."
    create_storage_monitor_function
    create_volume_ops_function
    create_svm_manager_function
    
    # Deploy functions
    print_status "Deploying functions..."
    deploy_function "netapp-storage-monitor" "NetApp storage monitoring and capacity reporting"
    deploy_function "netapp-volume-ops" "NetApp volume lifecycle operations"
    deploy_function "netapp-svm-manager" "NetApp Storage Virtual Machine management"
    
    # Test functions
    sleep 30  # Wait for functions to be ready
    test_functions
    
    print_success "NetApp MCP Knative Functions deployment completed!"
    print_status "Function URLs:"
    kn service list -n "${NAMESPACE}"
    
    print_status ""
    print_status "To test functions manually:"
    print_status "  kn func invoke netapp-storage-monitor --data '{\"operation\": \"get_clusters\"}'"
    print_status "  kn func invoke netapp-volume-ops --data '{\"operation\": \"create_volume\", \"volume_config\": {\"name\": \"test\"}}'"
    print_status "  kn func invoke netapp-svm-manager --data '{\"operation\": \"get_svms\"}'"
}

# Help function
show_help() {
    cat << EOF
NetApp ActiveIQ MCP Server - Knative Function Deployment Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -n, --namespace NAME    Kubernetes namespace (default: netapp-functions)
    -r, --registry URL      Container registry URL (default: your-registry.com/netapp)
    --no-build             Skip building container images
    --quiet                Reduce output verbosity

ENVIRONMENT VARIABLES:
    NETAPP_BASE_URL        NetApp ActiveIQ API endpoint (required)
    NETAPP_USERNAME        NetApp API username (required)
    NETAPP_PASSWORD        NetApp API password (required)
    NAMESPACE              Kubernetes namespace
    REGISTRY               Container registry URL

EXAMPLES:
    # Deploy with default settings
    export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
    export NETAPP_USERNAME="admin"
    export NETAPP_PASSWORD="password"
    $0

    # Deploy to custom namespace and registry
    $0 -n my-namespace -r my-registry.com/netapp

    # Deploy without building (use existing images)
    $0 --no-build

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        --no-build)
            BUILD_ARGS=""
            shift
            ;;
        --quiet)
            VERBOSE=""
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main
