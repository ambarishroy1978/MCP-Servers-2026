"""Server factory and utilities for MCP server creation."""

from .factory import create_mcp_server, register_tool, get_mcp_server, auto_discover_domains

__all__ = [
    "create_mcp_server",
    "register_tool",
    "get_mcp_server",
    "auto_discover_domains",
    "create_health_check_handler",
]
