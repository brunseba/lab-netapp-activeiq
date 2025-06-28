#!/bin/bash
set -euo pipefail

# NetApp ActiveIQ MCP Server - Knative Deployment Script
# This script automates the deployment of the MCP server to Knative

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="netapp-mcp-server"
NAMESPACE="netapp-mcp"
DEFAULT_REGISTRY="docker.io"
DEFAULT_IMAGE_TAG="latest"

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
    exit 1
}

# Function to check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "Command '$1' not found. Please install it first."
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check required commands
    check_command "kubectl"
    check_command "docker"
    check_command "kustomize"
    
    # Check optional commands
    if command -v "kn" &> /dev/null; then
        print_status "Knative CLI (kn) found"
    else
        print_warning "Knative CLI (kn) not found. Some features may not be available."
    fi
    
    # Check Kubernetes cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    fi
    
    # Check if Knative Serving is installed
    if ! kubectl get crd services.serving.knative.dev &> /dev/null; then
        print_error "Knative Serving not found. Please install Knative Serving first."
    fi
    
    print_success "Prerequisites check passed"
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy NetApp ActiveIQ MCP Server to Knative

OPTIONS:
    -h, --help                     Show this help message
    -n, --namespace NAMESPACE      Kubernetes namespace (default: netapp-mcp)
    -r, --registry REGISTRY        Container registry (default: docker.io)
    -t, --tag TAG                  Image tag (default: latest)
    -u, --netapp-url URL          NetApp ActiveIQ URL (required)
    -U, --netapp-user USER        NetApp username (required)
    -P, --netapp-password PASS    NetApp password (required)
    --build                       Build container image locally
    --push                        Push container image to registry
    --deploy-only                 Deploy only (skip build/push)
    --dry-run                     Show what would be deployed without applying
    --clean                       Remove existing deployment first

EXAMPLES:
    # Full deployment with build and push
    $0 --build --push \\
       --netapp-url "https://netapp.example.com/api" \\
       --netapp-user "admin" \\
       --netapp-password "password123"
    
    # Deploy only (assuming image already exists)
    $0 --deploy-only \\
       --registry "registry.company.com" \\
       --tag "1.0.0" \\
       --netapp-url "https://netapp.example.com/api" \\
       --netapp-user "admin" \\
       --netapp-password "password123"
    
    # Clean existing deployment
    $0 --clean

ENVIRONMENT VARIABLES:
    NETAPP_BASE_URL               NetApp ActiveIQ URL
    NETAPP_USERNAME               NetApp username
    NETAPP_PASSWORD               NetApp password
    CONTAINER_REGISTRY            Container registry
    IMAGE_TAG                     Image tag

EOF
}

# Function to build container image
build_image() {
    print_status "Building container image..."
    
    local image_name="${REGISTRY}/${PROJECT_NAME}:${IMAGE_TAG}"
    local build_date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    local vcs_ref=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    
    docker build \
        --build-arg BUILD_DATE="${build_date}" \
        --build-arg VCS_REF="${vcs_ref}" \
        --build-arg VERSION="${IMAGE_TAG}" \
        -t "${image_name}" \
        -t "${REGISTRY}/${PROJECT_NAME}:latest" \
        -f "${SCRIPT_DIR}/Dockerfile" \
        "${SCRIPT_DIR}"
    
    print_success "Container image built: ${image_name}"
}

# Function to push container image
push_image() {
    print_status "Pushing container image..."
    
    local image_name="${REGISTRY}/${PROJECT_NAME}:${IMAGE_TAG}"
    
    # Login to registry if credentials are available
    if [[ -n "${REGISTRY_USERNAME:-}" ]] && [[ -n "${REGISTRY_PASSWORD:-}" ]]; then
        echo "${REGISTRY_PASSWORD}" | docker login "${REGISTRY}" --username "${REGISTRY_USERNAME}" --password-stdin
    fi
    
    docker push "${image_name}"
    
    if [[ "${IMAGE_TAG}" != "latest" ]]; then
        docker push "${REGISTRY}/${PROJECT_NAME}:latest"
    fi
    
    print_success "Container image pushed: ${image_name}"
}

# Function to update configuration files
update_config() {
    print_status "Updating configuration files..."
    
    local temp_dir=$(mktemp -d)
    cp -r "${SCRIPT_DIR}/k8s" "${temp_dir}/"
    
    # Update namespace
    if [[ "${NAMESPACE}" != "netapp-mcp" ]]; then
        find "${temp_dir}/k8s" -name "*.yaml" -exec sed -i.bak "s/namespace: netapp-mcp/namespace: ${NAMESPACE}/g" {} \;
        find "${temp_dir}/k8s" -name "*.yaml" -exec sed -i.bak "s/name: netapp-mcp$/name: ${NAMESPACE}/g" {} \;
    fi
    
    # Update NetApp credentials in secret
    sed -i.bak "s|https://your-netapp-aiqum.example.com/api|${NETAPP_BASE_URL}|g" "${temp_dir}/k8s/secret.yaml"
    sed -i.bak "s|your-username|${NETAPP_USERNAME}|g" "${temp_dir}/k8s/secret.yaml"
    sed -i.bak "s|your-password|${NETAPP_PASSWORD}|g" "${temp_dir}/k8s/secret.yaml"
    
    # Update image reference
    local full_image="${REGISTRY}/${PROJECT_NAME}:${IMAGE_TAG}"
    sed -i.bak "s|image: netapp-mcp-server:latest|image: ${full_image}|g" "${temp_dir}/k8s/knative-service.yaml"
    
    # Update kustomization
    sed -i.bak "s|newTag: latest|newTag: ${IMAGE_TAG}|g" "${temp_dir}/k8s/kustomization.yaml"
    if [[ "${REGISTRY}" != "docker.io" ]]; then
        sed -i.bak "s|name: netapp-mcp-server|name: ${REGISTRY}/${PROJECT_NAME}|g" "${temp_dir}/k8s/kustomization.yaml"
    fi
    
    # Clean up backup files
    find "${temp_dir}/k8s" -name "*.bak" -delete
    
    echo "${temp_dir}/k8s"
}

# Function to deploy to Kubernetes
deploy() {
    print_status "Deploying to Kubernetes..."
    
    local config_dir=$(update_config)
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        print_status "Dry run - showing what would be deployed:"
        kubectl kustomize "${config_dir}"
        rm -rf "$(dirname "${config_dir}")"
        return
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply configuration
    kubectl apply -k "${config_dir}"
    
    # Clean up temp directory
    rm -rf "$(dirname "${config_dir}")"
    
    print_success "Deployment applied to namespace: ${NAMESPACE}"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Wait for deployment to be ready
    local max_wait=300
    local wait_time=0
    
    while [[ ${wait_time} -lt ${max_wait} ]]; do
        if kubectl get ksvc "${PROJECT_NAME}" -n "${NAMESPACE}" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null | grep -q "True"; then
            break
        fi
        
        print_status "Waiting for service to be ready... (${wait_time}s/${max_wait}s)"
        sleep 10
        wait_time=$((wait_time + 10))
    done
    
    if [[ ${wait_time} -ge ${max_wait} ]]; then
        print_error "Deployment verification timed out"
    fi
    
    # Show deployment status
    print_status "Deployment status:"
    kubectl get all -n "${NAMESPACE}"
    
    # Get service URL
    local service_url=$(kubectl get ksvc "${PROJECT_NAME}" -n "${NAMESPACE}" -o jsonpath='{.status.url}' 2>/dev/null || echo "N/A")
    print_success "Service deployed successfully!"
    print_status "Service URL: ${service_url}"
    
    # Show logs
    print_status "Recent logs:"
    kubectl logs -l app="${PROJECT_NAME}" -n "${NAMESPACE}" --tail=20 || true
}

# Function to clean deployment
clean_deployment() {
    print_status "Cleaning existing deployment..."
    
    if kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        kubectl delete namespace "${NAMESPACE}" --ignore-not-found=true
        print_success "Namespace ${NAMESPACE} deleted"
    else
        print_warning "Namespace ${NAMESPACE} not found"
    fi
}

# Main function
main() {
    # Default values
    NAMESPACE="${NAMESPACE:-netapp-mcp}"
    REGISTRY="${CONTAINER_REGISTRY:-${DEFAULT_REGISTRY}}"
    IMAGE_TAG="${IMAGE_TAG:-${DEFAULT_IMAGE_TAG}}"
    BUILD_IMAGE="false"
    PUSH_IMAGE="false"
    DEPLOY_ONLY="false"
    DRY_RUN="false"
    CLEAN="false"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
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
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -u|--netapp-url)
                NETAPP_BASE_URL="$2"
                shift 2
                ;;
            -U|--netapp-user)
                NETAPP_USERNAME="$2"
                shift 2
                ;;
            -P|--netapp-password)
                NETAPP_PASSWORD="$2"
                shift 2
                ;;
            --build)
                BUILD_IMAGE="true"
                shift
                ;;
            --push)
                PUSH_IMAGE="true"
                shift
                ;;
            --deploy-only)
                DEPLOY_ONLY="true"
                shift
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --clean)
                CLEAN="true"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                ;;
        esac
    done
    
    # Handle clean operation
    if [[ "${CLEAN}" == "true" ]]; then
        clean_deployment
        exit 0
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Get NetApp credentials from environment if not provided
    NETAPP_BASE_URL="${NETAPP_BASE_URL:-}"
    NETAPP_USERNAME="${NETAPP_USERNAME:-}"
    NETAPP_PASSWORD="${NETAPP_PASSWORD:-}"
    
    # Validate required parameters
    if [[ "${DEPLOY_ONLY}" == "false" ]] || [[ "${DRY_RUN}" == "false" ]]; then
        if [[ -z "${NETAPP_BASE_URL}" ]] || [[ -z "${NETAPP_USERNAME}" ]] || [[ -z "${NETAPP_PASSWORD}" ]]; then
            print_error "NetApp credentials are required. Use --netapp-url, --netapp-user, --netapp-password or set environment variables."
        fi
    fi
    
    print_status "Starting deployment with the following configuration:"
    print_status "  Namespace: ${NAMESPACE}"
    print_status "  Registry: ${REGISTRY}"
    print_status "  Image Tag: ${IMAGE_TAG}"
    print_status "  NetApp URL: ${NETAPP_BASE_URL}"
    print_status "  NetApp User: ${NETAPP_USERNAME}"
    
    # Build image if requested
    if [[ "${BUILD_IMAGE}" == "true" ]]; then
        build_image
    fi
    
    # Push image if requested
    if [[ "${PUSH_IMAGE}" == "true" ]]; then
        push_image
    fi
    
    # Deploy unless it's build-only
    if [[ "${DEPLOY_ONLY}" == "true" ]] || [[ "${BUILD_IMAGE}" == "true" ]] || [[ "${PUSH_IMAGE}" == "true" ]] || [[ "${DRY_RUN}" == "true" ]]; then
        deploy
        
        if [[ "${DRY_RUN}" == "false" ]]; then
            verify_deployment
        fi
    fi
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"
