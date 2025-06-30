# NetApp ActiveIQ Unified Manager MCP Server

This Model Context Protocol (MCP) server provides tools to interact with NetApp ActiveIQ Unified Manager REST API, enabling AI assistants to query and analyze NetApp storage infrastructure.

## Features

The MCP server provides comprehensive access to NetApp ActiveIQ Unified Manager including:

### Core Infrastructure
- **Clusters**: Query cluster information, configuration, and health status
- **Nodes**: Retrieve node details, performance metrics, and hardware information
- **Storage Virtual Machines (SVMs)**: Access SVM configuration and status
- **Volumes**: Get volume information, space usage, and performance analytics
- **Aggregates**: Monitor aggregate health and capacity

### Performance Monitoring
- **Cluster Performance**: Real-time and historical performance metrics
- **Volume Analytics**: IOPS, latency, and throughput analysis
- **Node Analytics**: Performance capacity and utilization tracking
- **Workload Monitoring**: Application workload performance and conformance

### Storage Management
- **Performance Service Levels**: Query and manage PSL policies
- **Storage Efficiency Policies**: Monitor compression and deduplication settings
- **QoS Policies**: Access Quality of Service configurations
- **Workloads**: Track storage workload performance and recommendations

### Operations
- **Events**: Query system events and alerts
- **Jobs**: Monitor background job status
- **System Information**: Get system health and version details

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r mcp_requirements.txt
   ```

2. **Configure Environment** (optional):
   ```bash
   export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
   export NETAPP_USERNAME="your-username"
   export NETAPP_PASSWORD="your-password"
   ```

3. **Add to MCP Client Configuration**:
   Update your MCP client configuration (e.g., Claude Desktop config):
   ```json
   {
     "mcpServers": {
       "netapp-activeiq": {
         "command": "python",
         "args": ["/path/to/mcp_server.py"],
         "env": {
           "NETAPP_BASE_URL": "https://your-netapp-aiqum.example.com/api",
           "NETAPP_USERNAME": "your-username",
           "NETAPP_PASSWORD": "your-password"
         }
       }
     }
   }
   ```

## Usage

### Initial Setup

First, configure the connection to your NetApp ActiveIQ Unified Manager:

```
configure_netapp_connection(
    base_url="https://your-netapp-aiqum.example.com/api",
    username="your-username",
    password="your-password",
    verify_ssl=True,
    timeout=30
)
```

### Common Use Cases

#### 1. Infrastructure Overview
```
# Get all clusters
get_clusters()

# Get cluster details
get_cluster_details("cluster-key")

# Get cluster performance
get_cluster_performance("cluster-key", interval="1d")
```

#### 2. Storage Analysis
```
# Get all volumes
get_volumes()

# Get volumes for specific SVM
get_volumes(svm_name="svm1")

# Get volume performance analytics
get_volume_analytics(cluster_name="cluster1", order_by="iops desc")
```

#### 3. Performance Monitoring
```
# Get nodes with performance metrics
get_nodes(cluster_name="cluster1")

# Get workload performance
get_workloads(conformance_status="non_conforming")

# Get performance service levels
get_performance_service_levels()
```

#### 4. Event and Alert Monitoring
```
# Get critical events
get_events(severity="critical", state="new")

# Get system jobs
get_jobs(state="running")

# Get system information
get_system_info()
```

## Available Tools

### Connection Management
- `configure_netapp_connection()` - Configure API connection

### Infrastructure
- `get_clusters()` - List all clusters
- `get_cluster_details()` - Get specific cluster details
- `get_cluster_performance()` - Get cluster performance metrics
- `get_nodes()` - List cluster nodes
- `get_svms()` - List Storage Virtual Machines
- `get_aggregates()` - List aggregates

### Storage
- `get_volumes()` - List volumes
- `get_volume_analytics()` - Get volume performance analytics

### Performance & Workloads
- `get_performance_service_levels()` - List Performance Service Levels
- `get_storage_efficiency_policies()` - List Storage Efficiency Policies
- `get_workloads()` - List storage workloads

### Operations
- `get_events()` - List system events
- `get_jobs()` - List system jobs
- `get_system_info()` - Get system information

## API Coverage

This MCP server implements key endpoints from the NetApp ActiveIQ Unified Manager API v2:

### Datacenter APIs
- `/datacenter/cluster/clusters` - Cluster management
- `/datacenter/cluster/nodes` - Node management
- `/datacenter/svm/svms` - SVM management
- `/datacenter/storage/volumes` - Volume management
- `/datacenter/storage/aggregates` - Aggregate management

### Storage Provider APIs
- `/storage-provider/performance-service-levels` - PSL management
- `/storage-provider/storage-efficiency-policies` - SEP management
- `/storage-provider/workloads` - Workload management

### Management Server APIs
- `/management-server/events` - Event management
- `/management-server/jobs` - Job management

### Admin APIs
- `/admin/system` - System information

## Performance Metrics

The server provides access to various performance metrics:

### Time Intervals
- `1h` - Last hour (5-minute samples)
- `12h` - Last 12 hours (5-minute samples)
- `1d` - Last day (5-minute samples)
- `2d` - Last 2 days (5-minute samples)
- `3d` - Last 3 days (5-minute samples)
- `15d` - Last 15 days (1-hour samples)
- `1w` - Last week (1-hour samples)
- `1m` - Last month (1-hour samples)
- `2m` - Last 2 months (1-hour samples)
- `3m` - Last 3 months (1-hour samples)
- `6m` - Last 6 months (1-hour samples)

### Metrics Types
- **IOPS**: Input/Output Operations Per Second
- **Latency**: Response time in milliseconds
- **Throughput**: Data transfer rate
- **Utilization**: Resource usage percentage
- **Performance Capacity**: Available vs. used performance

## Error Handling

The server includes comprehensive error handling:

- **Connection Errors**: Clear messages for authentication and network issues
- **API Errors**: Detailed HTTP status and error descriptions
- **Validation Errors**: Parameter validation with helpful messages
- **Timeout Handling**: Configurable request timeouts

## Security Considerations

- **Authentication**: Uses HTTP Basic Authentication
- **SSL/TLS**: Supports SSL certificate verification (configurable)
- **Credentials**: Supports environment variables for sensitive data
- **Timeouts**: Configurable request timeouts to prevent hanging

## Example Queries

### Find Storage Issues
```
# Get volumes with low space
get_volumes(order_by="space.available asc")

# Get non-conforming workloads
get_workloads(conformance_status="non_conforming")

# Get critical events
get_events(severity="critical", state="new")
```

### Performance Analysis
```
# Get top performing volumes
get_volume_analytics(order_by="iops desc", max_records=10)

# Get cluster performance over last week
get_cluster_performance("cluster-key", interval="1w")

# Get node utilization
get_nodes(order_by="performance_capacity.used desc")
```

### Capacity Planning
```
# Get aggregate space usage
get_aggregates(order_by="space.used desc")

# Get volume space utilization
get_volumes(order_by="space.used desc")

# Get workload space usage
get_workloads(order_by="space.used desc")
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify base_url is correct and includes `/api`
   - Check username/password credentials
   - Ensure network connectivity to ActiveIQ server

2. **SSL Certificate Errors**
   - Set `verify_ssl=False` for self-signed certificates
   - Or add certificate to trusted store

3. **Timeout Errors**
   - Increase timeout value
   - Check network latency to ActiveIQ server

4. **Permission Denied**
   - Verify user has required roles in ActiveIQ
   - Check API access permissions

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Temporal Workflows

This MCP server complements the existing Temporal workflows in your NetApp project:

- **Data Source**: Provides real-time data for workflow decisions
- **Monitoring**: Enables workflow health checks and performance validation
- **Event Driven**: Can trigger workflows based on ActiveIQ events
- **Validation**: Supports prerequisite validation for SVM/volume creation

## API Reference

For complete API documentation, refer to the NetApp ActiveIQ Unified Manager API Documentation at your ActiveIQ instance: `https://your-netapp-aiqum.example.com/docs/api`

## License

This MCP server is designed for use with NetApp ActiveIQ Unified Manager and follows NetApp's API terms of service.
