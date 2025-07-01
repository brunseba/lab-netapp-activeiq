# NetApp ActiveIQ consumption (temporal.io workflow / MCP Server) : Tech Survey

This repository is a technical survey around NetApp ActiveIQ usage to create filesharing service and manage Day2 operation through two complementary applications:

- **MCP Server**: AI assistant integration via Model Context Protocol
- **Temporal Workflows**: Durable execution for complex storage operations

## Project Structure

```
netapp/
├── apps/
│   ├── mcp/                    # MCP Server Application
│   │   ├── src/netapp_mcp_server/
│   │   ├── pyproject.toml
│   │   └── README.md
│   └── temporal/               # Temporal Workflows Application
│       ├── src/netapp_temporal_workflows/
│       ├── pyproject.toml
│       └── README.md
├── docs/                       # Documentation
├── k8s/                        # Kubernetes manifests
├── helm/                       # Helm charts
└── README.md                   # This file
```

## Applications

### MCP Server

The NetApp ActiveIQ MCP (Model Context Protocol) Server bridges NetApp's ActiveIQ Unified Manager API with AI assistants and automation tools through the standardized MCP protocol. This server enables AI applications to interact with NetApp storage infrastructure using natural language and structured queries.

### Temporal Workflows

Provides durable, fault-tolerant workflows for complex NetApp infrastructure operations including SVM creation, NFS provisioning, performance monitoring, and event processing.

## Key Features

- **MCP Protocol Compliance**: Full compliance with the Model Context Protocol specification and seamless integration with MCP-compatible AI assistants.
- **NetApp Integration**: Real-time access to storage metrics and events, supporting all major NetApp storage operations.
- **High Performance**: Async/await architecture for concurrent operations with built-in caching for frequently accessed data.
- **Enterprise Security**: Secure credential management, role-based access control integration, and SSL/TLS encryption.

## Temporal.io Integration

The NetApp ActiveIQ MCP Server integrates with Temporal.io to support complex workflows for infrastructure management. This includes workflows for creating Storage Virtual Machines (SVMs), provisioning NFS shares, monitoring performance, and processing system events.

### Key Temporal Workflows

- **SVM Creation:** Automates the creation and configuration of SVMs with validation and monitoring.
- **NFS Provisioning:** Manages NFS shares with detailed configuration steps.
- **Performance Monitoring:** Continuously monitors cluster performance and generates alerts based on thresholds.
- **Event Processing:** Handles system events by acknowledging them and sending notifications to the appropriate channels.

These workflows leverage Temporal's durable execution model, enabling robust, fault-tolerant operations for your storage environment.

### Installation

#### Requirements

- Python 3.10+
- Docker
- Kubernetes with Knative Serving
- Access to NetApp ActiveIQ Unified Manager

#### Setup with uv

1. Install uv (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/netapp/activeiq-mcp-server.git
   cd activeiq-mcp-server
   ```

3. Install MCP Server app:

   ```bash
   cd apps/mcp
   uv pip install -e .
   ```

4. Install Temporal Workflows app:

   ```bash
   cd ../temporal
   uv pip install -e .
   ```

### Usage

#### MCP Server

```bash
# Set environment variables
export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
export NETAPP_USERNAME="your-username"
export NETAPP_PASSWORD="your-password"

# Start the MCP server
netapp-mcp-server
```

#### Temporal Workflows

```bash
# Start the Temporal worker
netapp-temporal-worker
```

#### Configuration

Configure the connection to NetApp ActiveIQ Unified Manager using the `configure_netapp_connection` tool. Provide your base URL, username, password, SSL verification preference, and timeout settings.

#### Deploying to Knative

Use the provided `deploy-knative.sh` script to deploy the MCP server to a Knative-enabled Kubernetes cluster.

```bash
./deploy-knative.sh --build --push --netapp-url "https://netapp.example.com/api" --netapp-user "admin" --netapp-password "password123"
```

### Documentation

Comprehensive documentation can be found in the `docs` folder and is hosted at [https://netapp-mcp-server.docs/](https://netapp-mcp-server.docs/).

### Support

For any issues, please use the [GitHub Issues](https://github.com/netapp/activeiq-mcp-server/issues) page.

### License

Licensed under the Apache-2.0 License.
