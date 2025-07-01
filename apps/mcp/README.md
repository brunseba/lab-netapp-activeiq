# NetApp ActiveIQ MCP Server

Model Context Protocol (MCP) server for NetApp ActiveIQ Unified Manager, enabling AI assistants to interact with NetApp storage infrastructure.

## Features

- **MCP Protocol Compliance**: Full compliance with the Model Context Protocol specification
- **NetApp Integration**: Real-time access to storage metrics and events
- **High Performance**: Async/await architecture with built-in caching
- **Enterprise Security**: Secure credential management and SSL/TLS encryption

## Installation

```bash
# Install with uv
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"
```

## Usage

```bash
# Start the MCP server
netapp-mcp-server

# Or run directly
python -m netapp_mcp_server.start_mcp_server
```

## Configuration

Set environment variables:

```bash
export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
export NETAPP_USERNAME="your-username"
export NETAPP_PASSWORD="your-password"
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```
