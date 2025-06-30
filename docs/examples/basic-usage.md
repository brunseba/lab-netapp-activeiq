# Basic Usage Examples

This guide provides practical examples of using the NetApp ActiveIQ MCP Server with AI assistants and programmatic clients.

## Prerequisites

- NetApp ActiveIQ MCP Server running and accessible
- Valid NetApp credentials configured
- MCP client or AI assistant with MCP support

## Getting Started Examples

### 1. Test Your Connection

Before starting, verify your MCP server can connect to NetApp:

#### With AI Assistant (Claude Desktop)
```
"Test the connection to NetApp and show me the server status"
```

#### Programmatic Usage
```python
import asyncio
from mcp_client import MCPClient

async def test_setup():
    client = MCPClient("http://localhost:8080")

    # Test connection
    result = await client.call_tool("test_connection", {
        "include_details": True
    })

    print(f"Connection status: {result}")

asyncio.run(test_setup())
```

**Expected Response:**
```json
{
  "success": true,
  "connection_status": "healthy",
  "netapp_version": "9.12.1",
  "response_time_ms": 150,
  "details": {
    "um_host": "unified-manager.company.com",
    "api_version": "v2",
    "authenticated_user": "serviceaccount"
  }
}
```

## Basic Information Queries

### 2. List All Clusters

#### Natural Language (AI Assistant)
```
"Show me all the NetApp clusters and their current status"
```

#### Programmatic
```python
async def list_clusters():
    client = MCPClient("http://localhost:8080")

    clusters = await client.call_tool("get_clusters", {
        "fields": ["name", "state", "version", "nodes", "management_ip"]
    })

    print("Available Clusters:")
    for cluster in clusters["clusters"]:
        print(f"  - {cluster['name']}: {cluster['state']} (v{cluster['version']['full']})")

asyncio.run(list_clusters())
```

**Sample Output:**
```
Available Clusters:
  - prod-cluster-01: up (v9.12.1)
  - dev-cluster-02: up (v9.11.1)
  - test-cluster-03: up (v9.12.1)
```

### 3. Check Storage Volumes

#### Natural Language
```
"What volumes do we have and how much space is available?"
```

#### Programmatic
```python
async def check_volumes():
    client = MCPClient("http://localhost:8080")

    volumes = await client.call_tool("get_volumes", {
        "fields": ["name", "svm", "cluster", "size", "available", "used_percentage"],
        "max_records": 20
    })

    print("Volume Status:")
    print(f"{'Volume':<20} {'SVM':<15} {'Size (GB)':<10} {'Used %':<8} {'Available (GB)':<15}")
    print("-" * 80)

    for vol in volumes["volumes"]:
        size_gb = vol["size"]["total"] / (1024**3)
        avail_gb = vol["size"]["available"] / (1024**3)
        used_pct = vol["used_percentage"]

        print(f"{vol['name']:<20} {vol['svm']['name']:<15} {size_gb:<10.1f} {used_pct:<8.1f} {avail_gb:<15.1f}")

asyncio.run(check_volumes())
```

### 4. Monitor Storage Virtual Machines

#### Natural Language
```
"List all SVMs and show which protocols they support"
```

#### Programmatic
```python
async def list_svms():
    client = MCPClient("http://localhost:8080")

    svms = await client.call_tool("get_svms", {
        "fields": ["name", "state", "cluster", "protocols", "subtype"]
    })

    print("Storage Virtual Machines:")
    for svm in svms["svms"]:
        protocols = ", ".join(svm.get("protocols", []))
        print(f"  - {svm['name']} ({svm['cluster']['name']}): {svm['state']} | Protocols: {protocols}")

asyncio.run(list_svms())
```

## Monitoring and Alerting

### 5. Check for Critical Events

#### Natural Language
```
"Are there any critical alerts I should know about?"
```

#### Programmatic
```python
async def check_critical_events():
    client = MCPClient("http://localhost:8080")

    events = await client.call_tool("get_events", {
        "severity": "critical",
        "state": "new",
        "max_records": 10
    })

    if not events["events"]:
        print("✅ No critical events found!")
        return

    print("🚨 Critical Events:")
    for event in events["events"]:
        print(f"  - {event['name']}: {event['message']}")
        print(f"    Source: {event['source']['name']} | Time: {event['time']}")
        print()

asyncio.run(check_critical_events())
```

### 6. Storage Capacity Monitoring

#### Natural Language
```
"Show me volumes that are running low on space (over 80% full)"
```

#### Programmatic
```python
async def check_low_space():
    client = MCPClient("http://localhost:8080")

    low_space_volumes = await client.call_tool("get_volumes", {
        "utilization_threshold": 80,
        "fields": ["name", "svm", "cluster", "used_percentage", "size", "available"],
        "order_by": "used_percentage"
    })

    if not low_space_volumes["volumes"]:
        print("✅ No volumes with low space!")
        return

    print("⚠️  Volumes with Low Available Space (>80% used):")
    print(f"{'Volume':<20} {'SVM':<15} {'Used %':<8} {'Available':<12}")
    print("-" * 60)

    for vol in low_space_volumes["volumes"]:
        avail_gb = vol["size"]["available"] / (1024**3)
        print(f"{vol['name']:<20} {vol['svm']['name']:<15} {vol['used_percentage']:<8.1f}% {avail_gb:<12.1f} GB")

asyncio.run(check_low_space())
```

## Basic Management Operations

### 7. Create a Storage Virtual Machine

#### Natural Language
```
"Create a new SVM called 'dev-environment' on the production cluster with NFS protocol enabled"
```

#### Programmatic
```python
async def create_development_svm():
    client = MCPClient("http://localhost:8080")

    # First, get available clusters
    clusters = await client.call_tool("get_clusters", {
        "fields": ["name", "key", "state"]
    })

    # Find production cluster
    prod_cluster = None
    for cluster in clusters["clusters"]:
        if "prod" in cluster["name"].lower():
            prod_cluster = cluster["name"]
            break

    if not prod_cluster:
        print("❌ No production cluster found")
        return

    # Create SVM
    result = await client.call_tool("create_svm", {
        "name": "dev-environment",
        "cluster_name": prod_cluster,
        "protocols": ["nfs"],
        "security_style": "unix",
        "language": "c.utf_8"
    })

    if result["success"]:
        print(f"✅ SVM 'dev-environment' created successfully!")
        print(f"   Job ID: {result.get('job_id', 'N/A')}")
    else:
        print(f"❌ Failed to create SVM: {result['error']['message']}")

asyncio.run(create_development_svm())
```

### 8. Health Check Dashboard

#### Complete Health Check Script
```python
import asyncio
from datetime import datetime
from mcp_client import MCPClient

async def comprehensive_health_check():
    """
    Comprehensive health check that combines multiple monitoring aspects
    """
    client = MCPClient("http://localhost:8080")

    print("🔍 NetApp Infrastructure Health Check")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Test connection
    print("\n1. Testing NetApp Connection...")
    connection = await client.call_tool("test_connection", {})
    if connection["success"]:
        print("✅ NetApp connection: OK")
    else:
        print("❌ NetApp connection: FAILED")
        return

    # 2. Check cluster status
    print("\n2. Cluster Status...")
    clusters = await client.call_tool("get_clusters", {})
    healthy_clusters = 0
    for cluster in clusters["clusters"]:
        status = "✅" if cluster["state"] == "up" else "❌"
        print(f"   {status} {cluster['name']}: {cluster['state']}")
        if cluster["state"] == "up":
            healthy_clusters += 1

    print(f"   Summary: {healthy_clusters}/{len(clusters['clusters'])} clusters healthy")

    # 3. Check for critical events
    print("\n3. Critical Events...")
    events = await client.call_tool("get_events", {
        "severity": "critical",
        "state": "new",
        "max_records": 5
    })

    if not events["events"]:
        print("   ✅ No critical events")
    else:
        print(f"   ⚠️  {len(events['events'])} critical events found:")
        for event in events["events"][:3]:  # Show first 3
            print(f"      - {event['name']}")

    # 4. Check storage capacity
    print("\n4. Storage Capacity...")
    volumes = await client.call_tool("get_volumes", {
        "utilization_threshold": 85,
        "fields": ["name", "used_percentage"],
        "max_records": 5
    })

    if not volumes["volumes"]:
        print("   ✅ No volumes over 85% capacity")
    else:
        print(f"   ⚠️  {len(volumes['volumes'])} volumes over 85% capacity:")
        for vol in volumes["volumes"]:
            print(f"      - {vol['name']}: {vol['used_percentage']:.1f}%")

    # 5. SVM Status
    print("\n5. SVM Status...")
    svms = await client.call_tool("get_svms", {})
    running_svms = sum(1 for svm in svms["svms"] if svm["state"] == "running")
    print(f"   ✅ {running_svms}/{len(svms['svms'])} SVMs running")

    print("\n" + "=" * 60)
    print("Health check completed!")

# Run the health check
if __name__ == "__main__":
    asyncio.run(comprehensive_health_check())
```

## AI Assistant Integration Examples

### 9. Natural Language Queries

Here are examples of natural language queries you can use with AI assistants:

#### Infrastructure Discovery
- "What NetApp clusters do we have and what versions are they running?"
- "Show me all the storage virtual machines and their protocols"
- "List all volumes larger than 1TB"

#### Monitoring
- "Are there any critical alerts right now?"
- "Which volumes are running low on space?"
- "Show me the performance metrics for our production cluster"

#### Management
- "Create a new SVM for the development team with NFS support"
- "Show me the details of cluster 'prod-cluster-01'"
- "What aggregates are available on the production cluster?"

#### Analysis
- "Which SVMs are using the most storage?"
- "Show me all offline volumes"
- "What events happened in the last 24 hours?"

### 10. Error Handling Examples

```python
async def robust_volume_check():
    """
    Example of proper error handling with MCP tools
    """
    client = MCPClient("http://localhost:8080")

    try:
        # Attempt to get volume information
        volumes = await client.call_tool("get_volumes", {
            "max_records": 10
        })

        if not volumes["success"]:
            print(f"API Error: {volumes['error']['message']}")
            return

        print(f"Successfully retrieved {len(volumes['volumes'])} volumes")

    except ConnectionError:
        print("❌ Cannot connect to MCP server")
    except TimeoutError:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

asyncio.run(robust_volume_check())
```

## Configuration Examples

### 11. MCP Client Configuration

#### For Claude Desktop
```json
{
  "mcpServers": {
    "netapp-activeiq": {
      "command": "docker",
      "args": ["exec", "-i", "netapp-mcp-server", "python", "-m", "netapp_mcp_server", "--stdio"],
      "env": {
        "NETAPP_UM_HOST": "your-unified-manager.company.com",
        "NETAPP_USERNAME": "serviceaccount",
        "NETAPP_PASSWORD": "your-secure-password"
      }
    }
  }
}
```

#### For Custom Python Client
```python
from mcp_client import MCPClient

# Initialize client
client = MCPClient(
    server_url="http://localhost:8080",
    timeout=30,
    retry_attempts=3
)

# Use client
async def main():
    clusters = await client.call_tool("get_clusters", {})
    print(clusters)

asyncio.run(main())
```

## Useful Patterns

### 12. Periodic Monitoring

```python
import asyncio
import time

async def periodic_health_monitor(interval_seconds=300):
    """
    Run health checks every 5 minutes
    """
    client = MCPClient("http://localhost:8080")

    while True:
        try:
            print(f"\n🔍 Health Check - {datetime.now()}")

            # Quick health check
            events = await client.call_tool("get_events", {
                "severity": "critical",
                "state": "new"
            })

            if events["events"]:
                print(f"⚠️  {len(events['events'])} new critical events!")
                # Could send notifications here
            else:
                print("✅ No critical events")

        except Exception as e:
            print(f"❌ Health check failed: {e}")

        await asyncio.sleep(interval_seconds)

# Run continuous monitoring
# asyncio.run(periodic_health_monitor())
```

### 13. Batch Operations

```python
async def batch_cluster_info():
    """
    Gather comprehensive cluster information in batch
    """
    client = MCPClient("http://localhost:8080")

    # Run multiple queries concurrently
    tasks = [
        client.call_tool("get_clusters", {}),
        client.call_tool("get_svms", {}),
        client.call_tool("get_events", {"severity": "critical"}),
        client.call_tool("get_volumes", {"utilization_threshold": 80})
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    clusters, svms, events, low_space = results

    # Process results
    print("Comprehensive Infrastructure Report")
    print(f"Clusters: {len(clusters['clusters']) if isinstance(clusters, dict) else 'Error'}")
    print(f"SVMs: {len(svms['svms']) if isinstance(svms, dict) else 'Error'}")
    print(f"Critical Events: {len(events['events']) if isinstance(events, dict) else 'Error'}")
    print(f"Low Space Volumes: {len(low_space['volumes']) if isinstance(low_space, dict) else 'Error'}")

asyncio.run(batch_cluster_info())
```

## Next Steps

Now that you understand the basics:

1. **[Advanced Scenarios](advanced-scenarios.md)** - Complex workflows and automation
2. **[Architecture](../architecture/system-design.md)** - Understanding the system design
3. **[API Reference](../api/mcp-tools.md)** - Complete tool documentation
4. **[Deployment](../deployment/docker.md)** - Production deployment guide

## Common Issues

### Connection Problems
- Verify NetApp credentials are correct
- Check network connectivity to Unified Manager
- Ensure MCP server is running and accessible

### Authentication Issues
- Verify user has required NetApp roles
- Check password hasn't expired
- Ensure service account has proper permissions

### Performance Issues
- Use field filtering to reduce response size
- Implement caching for frequently accessed data
- Use appropriate max_records limits
