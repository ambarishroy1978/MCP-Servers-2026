#!/usr/bin/env python3
"""Entry point for running the MCP server with health check endpoint."""

import sys
import asyncio
from pathlib import Path
from typing import List, Optional

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from framework import get_app_logger, get_app_config, get_project_metadata, get_mcp_server
from framework.health.http_health import HealthCheckServer
from framework.middleware.middleware import HeaderCaptureMiddleware, PathPrefixMiddleware
from framework.core.config import app_config
from starlette.middleware import Middleware


async def start_health_server(host: str, port: int, mcp_server, base_path: str) -> None:
    """
    Start the health check server.
    
    Args:
        host: Server host
        port: Server port
        mcp_server: MCP server instance reference
        base_path: Base path for the server
    """
    try:
        health_server = HealthCheckServer(mcp_server_ref=mcp_server, base_path=base_path)
        logger = get_app_logger()
        
        path_prefix = f"/{base_path}" if base_path else ""
        logger.info(f"Health check endpoint: http://{host}:{port}{path_prefix}/health")
        
        await health_server.run(host=host, port=port)
    except Exception as e:
        logger = get_app_logger()
        logger.error(f"Health check server error: {e}", exc_info=True)
        raise


async def main_async() -> None:
    """Async main function to properly handle concurrent servers."""
    # Get MCP server instance (triggers auto-discovery)
    mcp = get_mcp_server()
    
    # Get framework instances
    logger = get_app_logger()
    config = get_app_config()
    project_metadata = get_project_metadata()
    
    # Build paths
    base_path = app_config.mcp_base_path
    path_prefix = f"/{base_path}" if base_path else ""
    mcp_path = f"{path_prefix}/mcp"
    
    # Log startup info
    project_version = project_metadata.get("version", "0.0.0")
    logger.info(f"Starting Next AI MCP Server v{project_version}")
    logger.info(f"Server configuration: {config}")
    
    # Create health server task
    health_task = asyncio.create_task(
        start_health_server(
            host=config["server_host"],
            port=config["health_check_port"],
            mcp_server=mcp,
            base_path=base_path
        )
    )
    
    # Wait briefly for health server startup
    await asyncio.sleep(0.5)
    
    # Log MCP endpoint
    logger.info(f"MCP Streamable HTTP endpoint: http://{config['server_host']}:{config['server_port']}{mcp_path}/")
    
    # Build middleware list
    middleware_list: List[Middleware] = []
    if base_path:
        middleware_list.append(Middleware(PathPrefixMiddleware, base_path=base_path))
    middleware_list.append(Middleware(HeaderCaptureMiddleware))
    
    # Configure log level
    log_level = config.get("log_level", "info").lower()
    
    # Run MCP server in a separate thread to avoid blocking
    import threading
    import concurrent.futures
    
    def run_mcp():
        """Run MCP server in thread."""
        mcp.run(
            host=config["server_host"],
            port=config["server_port"],
            transport="http",
            middleware=middleware_list,
            log_level=log_level
        )
    
    # Start MCP server in thread
    mcp_thread = threading.Thread(target=run_mcp, daemon=True)
    mcp_thread.start()
    
    try:
        # Keep health server running
        await health_task
    except KeyboardInterrupt:
        logger.info("Servers interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger = get_app_logger()
        logger.info("Shutdown requested")
    except Exception as e:
        logger = get_app_logger()
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger = get_app_logger()
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
