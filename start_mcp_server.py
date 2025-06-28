#!/usr/bin/env python3
"""
Startup script for NetApp ActiveIQ MCP Server

This script provides an easy way to start the MCP server with proper configuration.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["NETAPP_BASE_URL", "NETAPP_USERNAME", "NETAPP_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("The server will require manual configuration via configure_netapp_connection tool.")
        print("\nTo set them:")
        for var in missing_vars:
            if var == "NETAPP_BASE_URL":
                print(f"export {var}=\"https://your-netapp-aiqum.example.com/api\"")
            elif var == "NETAPP_USERNAME":
                print(f"export {var}=\"your-username\"")
            elif var == "NETAPP_PASSWORD":
                print(f"export {var}=\"your-password\"")
        print()

async def main():
    """Main function to start the MCP server"""
    setup_logging()
    check_environment()
    
    print("Starting NetApp ActiveIQ MCP Server...")
    print("=" * 50)
    
    # Import and run the MCP server
    try:
        from mcp_server import mcp
        import mcp.server.stdio
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp.run(read_stream, write_stream, mcp.create_initialization_options())
            
    except ImportError as e:
        print(f"Error importing MCP dependencies: {e}")
        print("Please install the required dependencies:")
        print("pip install -r mcp_requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
