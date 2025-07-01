# NetApp ActiveIQ MCP Server

The NetApp ActiveIQ MCP (Model Context Protocol) Server bridges NetApp's ActiveIQ Unified Manager API with AI assistants and automation tools through the standardized MCP protocol. This server enables AI applications to interact with NetApp storage infrastructure using natural language and structured queries.

## Key Features

- **MCP Protocol Compliance**: Full compliance with the Model Context Protocol specification and seamless integration with MCP-compatible AI assistants.
- **NetApp Integration**: Real-time access to storage metrics and events, supporting all major NetApp storage operations.
- **High Performance**: Async/await architecture for concurrent operations with built-in caching for frequently accessed data.
- **Enterprise Security**: Secure credential management, role-based access control integration, and SSL/TLS encryption.

## Installation

### Requirements

- Python 3.10+
- Docker
- Kubernetes with Knative Serving
- Access to NetApp ActiveIQ Unified Manager

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/netapp/activeiq-mcp-server.git
   cd activeiq-mcp-server
   ```

2. Configure your environment variables in `mcp_config.json`.

3. Install dependencies:

   ```bash
   pip install -r mcp_requirements.txt
   ```

4. Run using Docker:

   ```bash
   docker build -t netapp-mcp-server .
   docker run -p 8080:8080 netapp-mcp-server
   ```

## Usage

Start the MCP server:

```bash
python start_mcp_server.py
```

### Configuration

Configure the connection to NetApp ActiveIQ Unified Manager using the `configure_netapp_connection` tool. Provide your base URL, username, password, SSL verification preference, and timeout settings.

### Deploying to Knative

Use the provided `deploy-knative.sh` script to deploy the MCP server to a Knative-enabled Kubernetes cluster.

```bash
./deploy-knative.sh --build --push --netapp-url "https://netapp.example.com/api" --netapp-user "admin" --netapp-password "password123"
```

## Documentation

Comprehensive documentation can be found in the `docs` folder and is hosted at [https://netapp-mcp-server.docs/](https://netapp-mcp-server.docs/).

## Support

For any issues, please use the [GitHub Issues](https://github.com/netapp/activeiq-mcp-server/issues) page.

## License

Licensed under the Apache-2.0 License.
