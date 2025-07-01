#!/usr/bin/env python3
"""
Test script for NetApp ActiveIQ MCP Server

This script provides basic testing functionality for the MCP server.
It can be used to validate connections and basic functionality.
"""

import asyncio
import os
import sys
from mcp_server import NetAppConfig, NetAppClient

async def test_connection():
    """Test basic connection to NetApp ActiveIQ"""

    # Get configuration from environment variables or use defaults
    base_url = os.getenv("NETAPP_BASE_URL", "https://netapp-aiqum.example.com/api")
    username = os.getenv("NETAPP_USERNAME", "admin")
    password = os.getenv("NETAPP_PASSWORD", "password")

    print(f"Testing connection to: {base_url}")
    print(f"Username: {username}")

    # Create configuration
    config = NetAppConfig(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=False,  # For testing with self-signed certificates
        timeout=30
    )

    # Create client
    client = NetAppClient(config)

    try:
        # Test basic connection with clusters endpoint
        print("\n1. Testing cluster endpoint...")
        clusters = await client._make_request("GET", "/datacenter/cluster/clusters", {"max_records": 5})
        print(f"✓ Successfully retrieved {clusters.get('num_records', 0)} clusters")

        # Test system info endpoint
        print("\n2. Testing system info endpoint...")
        system_info = await client._make_request("GET", "/admin/system")
        print(f"✓ System info retrieved: {system_info.get('product', 'Unknown')}")

        # Test events endpoint
        print("\n3. Testing events endpoint...")
        events = await client._make_request("GET", "/management-server/events", {"max_records": 5})
        print(f"✓ Successfully retrieved {events.get('num_records', 0)} events")

        print("\n✓ All tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        return False

async def test_performance_endpoints():
    """Test performance-related endpoints"""

    config = NetAppConfig(
        base_url=os.getenv("NETAPP_BASE_URL", "https://netapp-aiqum.example.com/api"),
        username=os.getenv("NETAPP_USERNAME", "admin"),
        password=os.getenv("NETAPP_PASSWORD", "password"),
        verify_ssl=False,
        timeout=30
    )

    client = NetAppClient(config)

    try:
        # Test cluster analytics
        print("\n1. Testing cluster analytics...")
        cluster_analytics = await client._make_request("GET", "/datacenter/cluster/clusters/analytics", {"max_records": 5})
        print(f"✓ Cluster analytics: {cluster_analytics.get('num_records', 0)} records")

        # Test volume analytics
        print("\n2. Testing volume analytics...")
        volume_analytics = await client._make_request("GET", "/datacenter/storage/volumes/analytics", {"max_records": 5})
        print(f"✓ Volume analytics: {volume_analytics.get('num_records', 0)} records")

        # Test workloads
        print("\n3. Testing workloads...")
        workloads = await client._make_request("GET", "/storage-provider/workloads", {"max_records": 5})
        print(f"✓ Workloads: {workloads.get('num_records', 0)} records")

        print("\n✓ Performance tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Performance test failed: {e}")
        return False

def print_usage():
    """Print usage information"""
    print("""
NetApp ActiveIQ MCP Server Test Script

Usage:
    python test_mcp_server.py [test_type]

Test Types:
    connection    - Test basic API connection (default)
    performance   - Test performance endpoints
    all          - Run all tests

Environment Variables:
    NETAPP_BASE_URL  - Base URL for NetApp ActiveIQ API
    NETAPP_USERNAME  - Username for authentication
    NETAPP_PASSWORD  - Password for authentication

Example:
    export NETAPP_BASE_URL="https://your-netapp-aiqum.example.com/api"
    export NETAPP_USERNAME="your-username"
    export NETAPP_PASSWORD="your-password"
    python test_mcp_server.py connection
""")

async def main():
    """Main test function"""

    # Check for required environment variables
    required_vars = ["NETAPP_BASE_URL", "NETAPP_USERNAME", "NETAPP_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Using default values for testing...")

    # Get test type from command line
    test_type = sys.argv[1] if len(sys.argv) > 1 else "connection"

    if test_type == "help" or test_type == "-h" or test_type == "--help":
        print_usage()
        return

    print("NetApp ActiveIQ MCP Server Test")
    print("=" * 40)

    success = True

    if test_type in ["connection", "all"]:
        print("\nRunning connection tests...")
        success &= await test_connection()

    if test_type in ["performance", "all"]:
        print("\nRunning performance tests...")
        success &= await test_performance_endpoints()

    if test_type not in ["connection", "performance", "all"]:
        print(f"Unknown test type: {test_type}")
        print_usage()
        return

    print("\n" + "=" * 40)
    if success:
        print("All tests completed successfully!")
    else:
        print("Some tests failed. Check your configuration and network connectivity.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
