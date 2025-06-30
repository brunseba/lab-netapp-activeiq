# MCP Tools Reference

The NetApp ActiveIQ MCP Server provides a comprehensive set of tools that enable AI assistants to interact with NetApp storage infrastructure through the Model Context Protocol.

## Tool Categories

### 🔍 **Information & Discovery**
- [get_clusters](#get_clusters) - List and query cluster information
- [get_nodes](#get_nodes) - Get cluster node details
- [get_svms](#get_svms) - List Storage Virtual Machines
- [get_volumes](#get_volumes) - Query volume information
- [get_aggregates](#get_aggregates) - List storage aggregates
- [test_connection](#test_connection) - Test NetApp API connectivity

### 📊 **Monitoring & Performance**
- [get_cluster_performance](#get_cluster_performance) - Cluster performance metrics
- [get_volume_performance](#get_volume_performance) - Volume performance data
- [get_events](#get_events) - System events and alerts
- [get_capacity_info](#get_capacity_info) - Storage capacity information

### ⚙️ **Management Operations**
- [create_svm](#create_svm) - Create Storage Virtual Machine
- [create_volume](#create_volume) - Create new volume
- [modify_volume](#modify_volume) - Modify volume settings
- [create_snapshot](#create_snapshot) - Create volume snapshot

### 🚨 **Event Management**
- [acknowledge_event](#acknowledge_event) - Acknowledge system events
- [resolve_event](#resolve_event) - Resolve events
- [get_active_alerts](#get_active_alerts) - Get active alerts

## Tool Definitions

### get_clusters

List and query NetApp cluster information.

```json
{
  "name": "get_clusters",
  "description": "Retrieve information about NetApp ONTAP clusters",
  "inputSchema": {
    "type": "object",
    "properties": {
      "fields": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Specific fields to return",
        "default": ["name", "uuid", "version", "state", "management_ip"]
      },
      "query": {
        "type": "string",
        "description": "Filter clusters using query syntax (e.g., 'name:prod*')"
      },
      "max_records": {
        "type": "integer",
        "description": "Maximum number of records to return",
        "default": 20
      }
    }
  }
}
```

**Example Usage:**
```python
# Get all clusters with basic info
result = await mcp_client.call_tool("get_clusters", {})

# Get production clusters only
result = await mcp_client.call_tool("get_clusters", {
    "query": "name:prod*",
    "fields": ["name", "version", "state", "nodes"]
})
```

**Response:**
```json
{
  "clusters": [
    {
      "name": "prod-cluster-01",
      "uuid": "12345678-1234-1234-1234-123456789012",
      "version": {"full": "9.12.1"},
      "state": "up",
      "management_ip": "10.1.1.100",
      "nodes": 4
    }
  ],
  "total_records": 1
}
```

### get_svms

List Storage Virtual Machines (SVMs) with filtering options.

```json
{
  "name": "get_svms",
  "description": "Retrieve Storage Virtual Machine information",
  "inputSchema": {
    "type": "object",
    "properties": {
      "cluster_name": {
        "type": "string",
        "description": "Filter by cluster name"
      },
      "state": {
        "type": "string",
        "enum": ["running", "stopped", "starting", "stopping"],
        "description": "Filter by SVM state"
      },
      "protocols": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Filter by supported protocols (nfs, cifs, iscsi, fcp)"
      },
      "fields": {
        "type": "array",
        "items": {"type": "string"},
        "default": ["name", "uuid", "state", "cluster", "protocols"]
      }
    }
  }
}
```

### get_volumes

Query volume information with detailed filtering and sorting options.

```json
{
  "name": "get_volumes",
  "description": "Retrieve volume information and capacity details",
  "inputSchema": {
    "type": "object",
    "properties": {
      "svm_name": {
        "type": "string",
        "description": "Filter by SVM name"
      },
      "cluster_name": {
        "type": "string",
        "description": "Filter by cluster name"
      },
      "state": {
        "type": "string",
        "enum": ["online", "offline", "mixed"],
        "description": "Filter by volume state"
      },
      "size_threshold": {
        "type": "object",
        "properties": {
          "operator": {"type": "string", "enum": ["gt", "lt", "gte", "lte"]},
          "value": {"type": "integer"},
          "unit": {"type": "string", "enum": ["bytes", "kb", "mb", "gb", "tb"]}
        },
        "description": "Filter by volume size"
      },
      "utilization_threshold": {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "description": "Filter volumes above utilization percentage"
      },
      "order_by": {
        "type": "string",
        "enum": ["name", "size", "available", "used_percentage"],
        "default": "name"
      }
    }
  }
}
```

### create_svm

Create a new Storage Virtual Machine with specified configuration.

```json
{
  "name": "create_svm",
  "description": "Create a new Storage Virtual Machine (SVM)",
  "inputSchema": {
    "type": "object",
    "required": ["name", "cluster_name"],
    "properties": {
      "name": {
        "type": "string",
        "description": "Name for the new SVM"
      },
      "cluster_name": {
        "type": "string",
        "description": "Target cluster name"
      },
      "protocols": {
        "type": "array",
        "items": {"type": "string", "enum": ["nfs", "cifs", "iscsi", "fcp", "nvme"]},
        "default": ["nfs"],
        "description": "Protocols to enable"
      },
      "language": {
        "type": "string",
        "default": "c.utf_8",
        "description": "Language setting"
      },
      "security_style": {
        "type": "string",
        "enum": ["unix", "ntfs", "mixed"],
        "default": "unix",
        "description": "Security style"
      },
      "aggregates": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of aggregate names to assign"
      },
      "dns_config": {
        "type": "object",
        "properties": {
          "domains": {
            "type": "array",
            "items": {"type": "string"}
          },
          "servers": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    }
  }
}
```

### get_events

Retrieve system events with filtering and sorting capabilities.

```json
{
  "name": "get_events",
  "description": "Get system events and alerts",
  "inputSchema": {
    "type": "object",
    "properties": {
      "severity": {
        "type": "string",
        "enum": ["emergency", "alert", "critical", "error", "warning", "notice", "informational", "debug"],
        "description": "Filter by event severity"
      },
      "state": {
        "type": "string",
        "enum": ["new", "acknowledged", "resolved"],
        "description": "Filter by event state"
      },
      "source_type": {
        "type": "string",
        "enum": ["cluster", "node", "svm", "volume", "aggregate"],
        "description": "Filter by source object type"
      },
      "time_range": {
        "type": "object",
        "properties": {
          "start": {"type": "string", "format": "date-time"},
          "end": {"type": "string", "format": "date-time"}
        }
      },
      "max_records": {
        "type": "integer",
        "default": 50
      }
    }
  }
}
```

### test_connection

Test connectivity to NetApp ActiveIQ Unified Manager.

```json
{
  "name": "test_connection",
  "description": "Test connection to NetApp ActiveIQ Unified Manager",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include_details": {
        "type": "boolean",
        "default": false,
        "description": "Include detailed connection information"
      }
    }
  }
}
```

## Advanced Tool Usage

### Workflow Orchestration Tools

#### execute_temporal_workflow

Execute complex workflows using Temporal orchestration.

```json
{
  "name": "execute_temporal_workflow",
  "description": "Execute a predefined Temporal workflow",
  "inputSchema": {
    "type": "object",
    "required": ["workflow_name"],
    "properties": {
      "workflow_name": {
        "type": "string",
        "enum": ["svm_creation", "volume_provisioning", "data_migration", "backup_workflow"]
      },
      "parameters": {
        "type": "object",
        "description": "Workflow-specific parameters"
      },
      "timeout": {
        "type": "integer",
        "default": 3600,
        "description": "Workflow timeout in seconds"
      }
    }
  }
}
```

### Batch Operations

#### batch_operation

Execute multiple operations in a single request.

```json
{
  "name": "batch_operation",
  "description": "Execute multiple NetApp operations in batch",
  "inputSchema": {
    "type": "object",
    "required": ["operations"],
    "properties": {
      "operations": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["tool", "arguments"],
          "properties": {
            "tool": {"type": "string"},
            "arguments": {"type": "object"},
            "id": {"type": "string"}
          }
        }
      },
      "fail_on_error": {
        "type": "boolean",
        "default": false,
        "description": "Stop batch if any operation fails"
      }
    }
  }
}
```

## Error Handling

All tools follow consistent error response patterns:

```json
{
  "success": false,
  "error": {
    "code": "NETAPP_API_ERROR",
    "message": "Failed to retrieve cluster information",
    "details": {
      "http_status": 401,
      "netapp_error": "Authentication failed"
    }
  }
}
```

### Common Error Codes

- `AUTHENTICATION_FAILED` - Invalid credentials
- `AUTHORIZATION_DENIED` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `VALIDATION_ERROR` - Invalid input parameters
- `NETAPP_API_ERROR` - Error from NetApp API
- `TIMEOUT_ERROR` - Operation timed out
- `CONNECTION_ERROR` - Network connectivity issues

## Tool Usage Examples

### Natural Language Queries

With an AI assistant, you can use natural language:

**"Show me all volumes that are more than 80% full"**
```python
# Translates to:
mcp_client.call_tool("get_volumes", {
    "utilization_threshold": 80,
    "fields": ["name", "svm", "size", "used_percentage"]
})
```

**"Create a new SVM called 'dev-svm' on the production cluster with NFS protocol"**
```python
# Translates to:
mcp_client.call_tool("create_svm", {
    "name": "dev-svm",
    "cluster_name": "prod-cluster-01",
    "protocols": ["nfs"]
})
```

**"What are the current critical alerts?"**
```python
# Translates to:
mcp_client.call_tool("get_events", {
    "severity": "critical",
    "state": "new"
})
```

### Programmatic Usage

```python
import asyncio
from mcp_client import MCPClient

async def storage_health_check():
    client = MCPClient("http://localhost:8080")

    # Get cluster status
    clusters = await client.call_tool("get_clusters", {})

    # Check for volumes with low space
    low_space_volumes = await client.call_tool("get_volumes", {
        "utilization_threshold": 90,
        "fields": ["name", "svm", "cluster", "used_percentage", "available"]
    })

    # Get recent critical events
    critical_events = await client.call_tool("get_events", {
        "severity": "critical",
        "state": "new",
        "max_records": 10
    })

    return {
        "clusters": clusters,
        "low_space_volumes": low_space_volumes,
        "critical_events": critical_events
    }

# Run health check
health_status = asyncio.run(storage_health_check())
```

## Authentication

Tools automatically use the configured NetApp credentials. No additional authentication is required at the tool level.

## Rate Limiting

- Default rate limit: 100 requests per minute
- Configurable per tool type
- Automatic retry with exponential backoff
- Queue management for burst requests

## Caching

- Automatic caching for read operations
- Configurable TTL per tool type
- Cache invalidation on write operations
- Redis-based distributed caching

## Next Steps

- **[Architecture](../architecture/system-design.md)** - Understand the underlying architecture
- **[Examples](../examples/basic-usage.md)** - See practical usage examples
- **[Error Handling](error-handling.md)** - Learn about error handling patterns
- **[Authentication](authentication.md)** - Configure authentication methods
