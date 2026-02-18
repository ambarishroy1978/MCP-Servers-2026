"""
MCP Server Framework

This package contains the core framework components for building MCP servers.
Developers typically don't need to modify files in this package.
"""

# Import key framework components for easy access
from .core.utils import (
    MCPServerError,
    ToolExecutionError,
    APIError,
    ValidationError,
    setup_logging,
    get_uptime_seconds,
    get_app_config,
    set_app_config,
    get_app_logger,
    set_app_logger,
    get_project_metadata,
)

from .core.config import (
    Config,
    app_config,
    get_configuration,
    get_log_level,
    get_log_file,
    get_server_host,
    get_server_port,
    get_health_check_port,
    get_mcp_master_api_key,
    get_mcp_master_api_key_name,
)

from .decorators import (
    require_api_key,
    log_requests,
    handle_exceptions,
)

from .core.context import (
    get_request_context,
    set_request_context,
    get_api_key_from_context,
)

from .server import (
    create_mcp_server,
    register_tool,
    get_mcp_server,
    auto_discover_domains,
)

__all__ = [
    # Core utilities
    "MCPServerError",
    "ToolExecutionError", 
    "APIError",
    "ValidationError",
    "setup_logging",
    "get_uptime_seconds",
    "get_app_config",
    "set_app_config",
    "get_app_logger",
    "set_app_logger",
    "handle_exceptions",
    "get_project_metadata",
    
    # Configuration
    "Config",
    "app_config",
    "get_configuration",
    "get_log_level",
    "get_log_file",
    "get_server_host",
    "get_server_port",
    "get_health_check_port",
    "get_mcp_master_api_key",
    "get_mcp_master_api_key_name",
    
    # Decorators
    "require_api_key",
    "log_requests", 
    "handle_exceptions",
    
    # Context
    "get_request_context",
    "set_request_context",
    "get_api_key_from_context",
    
    # Server factory
    "create_mcp_server",
    "register_tool",
    "get_mcp_server",
    "auto_discover_domains",
]
