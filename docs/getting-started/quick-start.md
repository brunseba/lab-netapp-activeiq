# Quick Start Guide

Get your NetApp ActiveIQ MCP Server up and running in 5 minutes!

## Prerequisites

Before starting, ensure you have:

- ✅ **Docker** installed and running
- ✅ **NetApp ActiveIQ Unified Manager** accessible
- ✅ **Valid credentials** with appropriate permissions
- ✅ **Python 3.8+** (for development setup)

## Option 1: Docker Quick Start (Recommended)

### 1. Pull the Docker Image

```bash
docker pull netapp/activeiq-mcp-server:latest
```

### 2. Create Configuration File

Create a `.env` file with your NetApp credentials:

```bash
# NetApp ActiveIQ Configuration
NETAPP_UM_HOST=your-unified-manager.company.com
NETAPP_USERNAME=admin
NETAPP_PASSWORD=your-secure-password

# MCP Server Configuration  
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
LOG_LEVEL=INFO

# Optional: Temporal Integration
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
```

### 3. Run the Server

```bash
docker run -d \
  --name netapp-mcp-server \
  --env-file .env \
  -p 8080:8080 \
  netapp/activeiq-mcp-server:latest
```

### 4. Verify Installation

```bash
# Check server status
curl http://localhost:8080/health

# List available MCP tools
curl http://localhost:8080/tools
```

## Option 2: Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/netapp/activeiq-mcp-server.git
cd activeiq-mcp-server
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your NetApp credentials
```

### 4. Run the Server

```bash
python -m netapp_mcp_server
```

## First Steps with MCP Tools

### 1. Test Connection

```bash
# Test NetApp connection
curl -X POST http://localhost:8080/tools/test_connection \
  -H "Content-Type: application/json"
```

### 2. Get Cluster Information

```bash
# List all clusters
curl -X POST http://localhost:8080/tools/get_clusters \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"fields": ["name", "version", "state"]}}'
```

### 3. Monitor Storage

```bash
# Get volume information
curl -X POST http://localhost:8080/tools/get_volumes \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"max_records": 10}}'
```

## Connect with AI Assistant

### Using with Claude Desktop

1. Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "netapp-activeiq": {
      "command": "docker",
      "args": ["exec", "-i", "netapp-mcp-server", "python", "-m", "netapp_mcp_server", "--stdio"],
      "env": {
        "NETAPP_UM_HOST": "your-unified-manager.company.com",
        "NETAPP_USERNAME": "admin", 
        "NETAPP_PASSWORD": "your-secure-password"
      }
    }
  }
}
```

2. Restart Claude Desktop

3. Try natural language queries:
   - "Show me the health status of all clusters"
   - "What volumes are running low on space?"
   - "Create a new SVM for the production environment"

### Using with Other MCP Clients

The server implements the standard MCP protocol and can be used with any MCP-compatible client. See the [MCP Protocol documentation](https://modelcontextprotocol.io/) for integration details.

## Verification Checklist

After setup, verify everything is working:

- [ ] Server starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] NetApp connection test succeeds  
- [ ] MCP tools are listed correctly
- [ ] Sample queries return data
- [ ] AI assistant can communicate with server

## Common Issues

### Connection Issues

**Problem**: Cannot connect to NetApp Unified Manager
```bash
# Check network connectivity
curl -k https://your-unified-manager.company.com/api/v2/datacenter/cluster/clusters

# Verify credentials
curl -k -u "username:password" https://your-unified-manager.company.com/api/v2/datacenter/cluster/clusters
```

### Authentication Issues

**Problem**: 401 Unauthorized responses
- Verify username/password in .env file
- Check user has required roles (Operator, Storage Administrator, or Application Administrator)
- Ensure account is not locked

### Docker Issues

**Problem**: Container won't start
```bash
# Check logs
docker logs netapp-mcp-server

# Check environment variables
docker exec netapp-mcp-server env | grep NETAPP
```

## Next Steps

Now that your server is running:

1. **[Learn the Architecture](../architecture/system-design.md)** - Understand how it works
2. **[Explore API Tools](../api/mcp-tools.md)** - See all available operations  
3. **[Try Examples](../examples/basic-usage.md)** - Follow guided examples
4. **[Deploy to Production](../deployment/docker.md)** - Production deployment guide

## Getting Help

- 📖 **Documentation**: Browse this documentation site
- 🐛 **Issues**: Report problems on GitHub
- 💬 **Discussions**: Join our community discussions
- 📧 **Support**: Contact NetApp support for enterprise assistance
