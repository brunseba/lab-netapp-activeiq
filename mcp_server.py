#!/usr/bin/env python3
"""
NetApp ActiveIQ Unified Manager MCP Server

This Model Context Protocol (MCP) server provides tools to interact with 
NetApp ActiveIQ Unified Manager REST API. It enables AI assistants to:
- Query cluster information and performance metrics
- Retrieve SVM (Storage Virtual Machine) details
- Access volume information and analytics
- Monitor storage efficiency and QoS policies
- Manage workloads and performance service levels

Based on NetApp ActiveIQ Unified Manager API v2
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlencode

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Server initialization
mcp = FastMCP("NetApp ActiveIQ MCP Server")

# Configuration models
class NetAppConfig(BaseModel):
    """Configuration for NetApp ActiveIQ connection"""
    base_url: str = Field(..., description="Base URL for NetApp ActiveIQ API")
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    timeout: int = Field(default=30, description="Request timeout in seconds")

class NetAppClient:
    """Client for NetApp ActiveIQ Unified Manager API"""
    
    def __init__(self, config: NetAppConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.timeout = httpx.Timeout(config.timeout)
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to NetApp API"""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
        
        auth = (self.config.username, self.config.password)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(
            verify=self.config.verify_ssl,
            timeout=self.timeout,
            auth=auth
        ) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=headers
                )
                response.raise_for_status()
                return response.json() if response.content else {}
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise

# Global client instance
_netapp_client: Optional[NetAppClient] = None

def get_client() -> NetAppClient:
    """Get the NetApp client instance"""
    global _netapp_client
    
    # Auto-configure from environment variables if not already configured
    if _netapp_client is None:
        base_url = os.getenv("NETAPP_BASE_URL")
        username = os.getenv("NETAPP_USERNAME")
        password = os.getenv("NETAPP_PASSWORD")
        
        if base_url and username and password:
            logger.info("Auto-configuring NetApp client from environment variables")
            config = NetAppConfig(
                base_url=base_url,
                username=username,
                password=password,
                verify_ssl=os.getenv("NETAPP_VERIFY_SSL", "true").lower() == "true",
                timeout=int(os.getenv("NETAPP_TIMEOUT", "30"))
            )
            _netapp_client = NetAppClient(config)
        else:
            raise RuntimeError("NetApp client not configured. Use configure_netapp_connection first or set environment variables (NETAPP_BASE_URL, NETAPP_USERNAME, NETAPP_PASSWORD).")
    
    return _netapp_client

@mcp.tool()
async def configure_netapp_connection(
    base_url: str,
    username: str, 
    password: str,
    verify_ssl: bool = True,
    timeout: int = 30
) -> str:
    """
    Configure connection to NetApp ActiveIQ Unified Manager.
    
    Args:
        base_url: Base URL for NetApp ActiveIQ API (e.g., https://netapp-aiqum.example.com/api)
        username: Username for authentication
        password: Password for authentication  
        verify_ssl: Whether to verify SSL certificates (default: True)
        timeout: Request timeout in seconds (default: 30)
    
    Returns:
        Confirmation message
    """
    global _netapp_client
    
    config = NetAppConfig(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        timeout=timeout
    )
    
    _netapp_client = NetAppClient(config)
    
    # Test connection
    try:
        await _netapp_client._make_request("GET", "/datacenter/cluster/clusters", {"max_records": 1})
        return f"Successfully connected to NetApp ActiveIQ at {base_url}"
    except Exception as e:
        _netapp_client = None
        return f"Failed to connect to NetApp ActiveIQ: {e}"

@mcp.tool()
async def get_clusters(
    name: Optional[str] = None,
    location: Optional[str] = None,
    version_generation: Optional[int] = None,
    max_records: int = 100,
    order_by: str = "name"
) -> str:
    """
    Retrieve list of ONTAP clusters from NetApp ActiveIQ.
    
    Args:
        name: Filter by cluster name
        location: Filter by cluster location
        version_generation: Filter by ONTAP version generation (e.g., 9)
        max_records: Maximum number of records to return (default: 100)
        order_by: Sort field (default: name)
    
    Returns:
        JSON string containing cluster information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if name:
        params["name"] = name
    if location:
        params["location"] = location
    if version_generation:
        params["version.generation"] = version_generation
    
    result = await client._make_request("GET", "/datacenter/cluster/clusters", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_cluster_details(cluster_key: str) -> str:
    """
    Get detailed information about a specific cluster.
    
    Args:
        cluster_key: Unique identifier of the cluster
    
    Returns:
        JSON string containing detailed cluster information
    """
    client = get_client()
    
    endpoint = f"/datacenter/cluster/clusters/{cluster_key}"
    result = await client._make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_cluster_performance(
    cluster_key: str,
    interval: str = "1h"
) -> str:
    """
    Get performance metrics for a specific cluster.
    
    Args:
        cluster_key: Unique identifier of the cluster
        interval: Time range for metrics (1h, 12h, 1d, 2d, 3d, 15d, 1w, 1m, 2m, 3m, 6m)
    
    Returns:
        JSON string containing performance metrics
    """
    client = get_client()
    
    endpoint = f"/datacenter/cluster/clusters/{cluster_key}/metrics"
    params = {"interval": interval}
    
    result = await client._make_request("GET", endpoint, params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_nodes(
    cluster_name: Optional[str] = None,
    name: Optional[str] = None,
    model: Optional[str] = None,
    health: Optional[bool] = None,
    max_records: int = 100,
    order_by: str = "name"
) -> str:
    """
    Retrieve list of nodes from NetApp clusters.
    
    Args:
        cluster_name: Filter by cluster name
        name: Filter by node name
        model: Filter by node model
        health: Filter by node health status
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing node information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if cluster_name:
        params["cluster.name"] = cluster_name
    if name:
        params["name"] = name
    if model:
        params["model"] = model
    if health is not None:
        params["health"] = health
    
    result = await client._make_request("GET", "/datacenter/cluster/nodes", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_svms(
    cluster_name: Optional[str] = None,
    name: Optional[str] = None,
    state: Optional[str] = None,
    max_records: int = 100,
    order_by: str = "name"
) -> str:
    """
    Retrieve list of Storage Virtual Machines (SVMs).
    
    Args:
        cluster_name: Filter by cluster name
        name: Filter by SVM name
        state: Filter by SVM state (running, stopped, etc.)
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing SVM information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if cluster_name:
        params["cluster.name"] = cluster_name
    if name:
        params["name"] = name
    if state:
        params["state"] = state
    
    result = await client._make_request("GET", "/datacenter/svm/svms", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_volumes(
    cluster_name: Optional[str] = None,
    svm_name: Optional[str] = None,
    name: Optional[str] = None,
    state: Optional[str] = None,
    style: Optional[str] = None,
    max_records: int = 100,
    order_by: str = "name"
) -> str:
    """
    Retrieve list of volumes.
    
    Args:
        cluster_name: Filter by cluster name
        svm_name: Filter by SVM name
        name: Filter by volume name
        state: Filter by volume state (online, offline, etc.)
        style: Filter by volume style (flexvol, flexgroup)
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing volume information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if cluster_name:
        params["cluster.name"] = cluster_name
    if svm_name:
        params["svm.name"] = svm_name
    if name:
        params["name"] = name
    if state:
        params["state"] = state
    if style:
        params["style"] = style
    
    result = await client._make_request("GET", "/datacenter/storage/volumes", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_volume_analytics(
    cluster_name: Optional[str] = None,
    svm_name: Optional[str] = None,
    volume_name: Optional[str] = None,
    period: Optional[int] = None,
    max_records: int = 100,
    order_by: str = "iops desc"
) -> str:
    """
    Get volume performance analytics.
    
    Args:
        cluster_name: Filter by cluster name
        svm_name: Filter by SVM name  
        volume_name: Filter by volume name
        period: Duration of aggregation in hours
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing volume analytics
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if cluster_name:
        params["cluster.name"] = cluster_name
    if svm_name:
        params["svm.name"] = svm_name
    if volume_name:
        params["volume.name"] = volume_name
    if period:
        params["period"] = period
    
    result = await client._make_request("GET", "/datacenter/storage/volumes/analytics", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_aggregates(
    cluster_name: Optional[str] = None,
    name: Optional[str] = None,
    state: Optional[str] = None,
    type_filter: Optional[str] = None,
    max_records: int = 100,
    order_by: str = "name"
) -> str:
    """
    Retrieve list of aggregates.
    
    Args:
        cluster_name: Filter by cluster name
        name: Filter by aggregate name
        state: Filter by aggregate state
        type_filter: Filter by aggregate type
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing aggregate information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if cluster_name:
        params["cluster.name"] = cluster_name
    if name:
        params["name"] = name
    if state:
        params["state"] = state
    if type_filter:
        params["type"] = type_filter
    
    result = await client._make_request("GET", "/datacenter/storage/aggregates", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_performance_service_levels(
    name: Optional[str] = None,
    system_defined: Optional[bool] = None,
    max_records: int = 100,
    order_by: str = "name"
) -> str:
    """
    Retrieve Performance Service Levels.
    
    Args:
        name: Filter by PSL name
        system_defined: Filter by system-defined PSLs
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing Performance Service Level information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if name:
        params["name"] = name
    if system_defined is not None:
        params["system_defined"] = system_defined
    
    result = await client._make_request("GET", "/storage-provider/performance-service-levels", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_storage_efficiency_policies(
    name: Optional[str] = None,
    system_defined: Optional[bool] = None,
    max_records: int = 100,
    order_by: str = "name"
) -> str:
    """
    Retrieve Storage Efficiency Policies.
    
    Args:
        name: Filter by policy name
        system_defined: Filter by system-defined policies
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing Storage Efficiency Policy information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if name:
        params["name"] = name
    if system_defined is not None:
        params["system_defined"] = system_defined
    
    result = await client._make_request("GET", "/storage-provider/storage-efficiency-policies", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_workloads(
    cluster_name: Optional[str] = None,
    svm_name: Optional[str] = None,
    workload_type: Optional[str] = None,
    conformance_status: Optional[str] = None,
    max_records: int = 100,
    order_by: str = "name"
) -> str:
    """
    Retrieve workloads information.
    
    Args:
        cluster_name: Filter by cluster name
        svm_name: Filter by SVM name
        workload_type: Filter by workload type (file_share, lun, unknown)
        conformance_status: Filter by conformance status
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing workload information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if cluster_name:
        params["cluster.name"] = cluster_name
    if svm_name:
        params["svm.name"] = svm_name
    if workload_type:
        params["type"] = workload_type
    if conformance_status:
        params["conformance_status"] = conformance_status
    
    result = await client._make_request("GET", "/storage-provider/workloads", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_events(
    severity: Optional[str] = None,
    state: Optional[str] = None,
    source_type: Optional[str] = None,
    max_records: int = 100,
    order_by: str = "create_time desc"
) -> str:
    """
    Retrieve events from NetApp ActiveIQ.
    
    Args:
        severity: Filter by event severity (critical, error, warning, information)
        state: Filter by event state (new, acknowledged, resolved, obsolete)
        source_type: Filter by source type
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing event information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if severity:
        params["severity"] = severity
    if state:
        params["state"] = state
    if source_type:
        params["source_type"] = source_type
    
    result = await client._make_request("GET", "/management-server/events", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_jobs(
    state: Optional[str] = None,
    type_filter: Optional[str] = None,
    max_records: int = 100,
    order_by: str = "create_time desc"
) -> str:
    """
    Retrieve job information.
    
    Args:
        state: Filter by job state
        type_filter: Filter by job type
        max_records: Maximum number of records to return
        order_by: Sort field
    
    Returns:
        JSON string containing job information
    """
    client = get_client()
    
    params = {
        "max_records": max_records,
        "order_by": order_by
    }
    
    if state:
        params["state"] = state
    if type_filter:
        params["type"] = type_filter
    
    result = await client._make_request("GET", "/management-server/jobs", params)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_system_info() -> str:
    """
    Get system information about NetApp ActiveIQ Unified Manager.
    
    Returns:
        JSON string containing system information
    """
    client = get_client()
    
    result = await client._make_request("GET", "/admin/system")
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Run the MCP server
    import mcp.server.stdio
    
    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp.run(read_stream, write_stream, mcp.create_initialization_options())
    
    asyncio.run(main())
