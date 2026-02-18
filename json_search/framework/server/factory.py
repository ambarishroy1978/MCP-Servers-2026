"""MCP server factory and tool registration utilities."""

import importlib
import sys
from pathlib import Path
from typing import Callable, Optional
from dotenv import load_dotenv

from fastmcp import FastMCP
from ..core.config import app_config
from .. import (
    setup_logging,
    get_project_metadata,
    set_app_config,
    set_app_logger,
    get_configuration,
    require_api_key,
    log_requests,
    handle_exceptions,
    get_app_logger,
)

# Module state
_global_server: Optional[FastMCP] = None
_domains_discovered: bool = False


def create_mcp_server() -> FastMCP:
    """
    Create and configure a FastMCP server instance with all framework setup.
    
    This function handles all the framework initialization:
    - Environment loading
    - Configuration setup
    - Logging initialization
    - Server instance creation
    
    Returns:
        Configured FastMCP server instance ready for tool registration
        
    Raises:
        RuntimeError: If server creation fails
    """
    try:
        # Load environment variables
        load_dotenv()

        # Get configuration
        config = get_configuration()

        # Set up logging
        logger = setup_logging(
            log_level=app_config.log_level,
            log_file=app_config.log_file
        )

        # Initialize application-level config and logger
        set_app_config(config)
        set_app_logger(logger)

        # Get project metadata
        project_metadata = get_project_metadata()

        # Initialize FastMCP server
        mcp = FastMCP(
            name=project_metadata.get("name", "Next AI MCP Server")
        )
        mcp.description = project_metadata.get("description", "MCP Server")
        
        logger.info("MCP server instance created and configured")
        
        return mcp
    except Exception as e:
        raise RuntimeError(f"Failed to create MCP server: {e}") from e


def auto_discover_domains() -> None:
    """
    Auto-discover and import domain server modules from the src/ directory.
    
    This function scans the src/ directory for subdirectories containing a server.py file
    and automatically imports them to trigger tool registration.
    """
    global _domains_discovered
    if _domains_discovered:
        return
    
    logger = get_app_logger()
    logger.info("Starting domain auto-discovery...")
    
    # Get the src directory path
    src_path = Path("src")
    if not src_path.exists() or not src_path.is_dir():
        logger.warning("src/ directory not found, skipping domain discovery")
        _domains_discovered = True
        return
    
    discovered_domains = []
    failed_domains = []
    
    # Scan for domain directories
    try:
        for item in sorted(src_path.iterdir()):
            if not item.is_dir():
                continue
                
            # Skip special directories
            if item.name.startswith(('_', '.')) or item.name.endswith('.egg-info'):
                continue
                
            # Check if it has a server.py file
            server_file = item / "server.py"
            if not server_file.exists():
                continue
                
            # Try to import the domain's server module
            module_name = f"src.{item.name}.server"
            try:
                importlib.import_module(module_name)
                discovered_domains.append(item.name)
                logger.info(f"Registered domain: {item.name}")
            except ImportError as e:
                failed_domains.append((item.name, f"Import error: {e}"))
                logger.error(f"Failed to load domain '{item.name}': {e}")
            except Exception as e:
                failed_domains.append((item.name, f"Unexpected error: {type(e).__name__}: {e}"))
                logger.error(f"Unexpected error loading domain '{item.name}': {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error during domain discovery: {e}", exc_info=True)
    
    # Summary logging
    if discovered_domains:
        logger.info(f"Domain discovery complete. Registered {len(discovered_domains)} domain(s): {', '.join(discovered_domains)}")
    
    if failed_domains:
        logger.warning(f"Failed to load {len(failed_domains)} domain(s)")
        for domain, error in failed_domains:
            logger.debug(f"  - {domain}: {error}")
    
    if not discovered_domains and not failed_domains:
        logger.warning("No domains found. Ensure domain directories contain server.py files.")
    
    _domains_discovered = True


def get_mcp_server() -> FastMCP:
    """
    Get the global MCP server instance, creating it if needed.
    
    This function provides access to the framework-managed global server instance.
    The server is created lazily on first access with all framework setup applied.
    It also triggers auto-discovery of domains on first access.
    
    Returns:
        The global FastMCP server instance
        
    Raises:
        RuntimeError: If server creation fails
    """
    global _global_server
    if _global_server is None:
        _global_server = create_mcp_server()
        # Auto-discover domains after server creation
        auto_discover_domains()
    return _global_server


def register_tool(tool_name: str) -> Callable:
    """
    Decorator to register a tool with the global MCP server.
    
    Automatically applies framework decorators:
    - FastMCP tool registration
    - Request logging
    - API key authentication
    - Exception handling
    
    Args:
        tool_name: Name of the tool for error handling
        
    Returns:
        Decorator function
        
    Example:
        @register_tool("my_tool")
        async def my_tool_handler(params: MyParams):
            return await my_tool_function(params.param1, params.param2)
    """
    def decorator(func: Callable) -> Callable:
        # Get the global server instance
        server = get_mcp_server()
        
        # Apply decorators in correct order - server.tool() must be LAST
        decorated_func = handle_exceptions(tool_name)(func)
        decorated_func = require_api_key(decorated_func)
        decorated_func = log_requests(decorated_func)
        decorated_func = server.tool()(decorated_func)
        
        return decorated_func
    
    return decorator
