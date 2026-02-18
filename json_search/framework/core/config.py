"""Configuration management for the MCP server."""

import os
from typing import Any, Dict, Optional


class Config:
    """
    Configuration class that provides type-safe access to configuration values.
    Eliminates the need for hardcoded configuration key strings throughout the codebase.
    """
    
    def __init__(self):
        """Initialize configuration with validation."""
        self._validate_environment()
    
    def _validate_environment(self) -> None:
        """Validate environment variables on initialization."""
        # Validate port numbers
        for port_var, port_name in [("SERVER_PORT", "server port"), ("HEALTH_CHECK_PORT", "health check port")]:
            port_value = os.getenv(port_var)
            if port_value:
                try:
                    port = int(port_value)
                    if not 1 <= port <= 65535:
                        raise ValueError(f"{port_name} must be between 1 and 65535")
                except ValueError as e:
                    raise ValueError(f"Invalid {port_name} '{port_value}': {e}")
    
    @property
    def log_level(self) -> str:
        """Get the logging level."""
        return os.getenv("LOG_LEVEL", "INFO").upper()
    
    @property
    def log_file(self) -> Optional[str]:
        """Get the log file path."""
        return os.getenv("LOG_FILE")
    
    @property
    def server_host(self) -> str:
        """Get the server host."""
        return os.getenv("SERVER_HOST", "localhost")
    
    @property
    def server_port(self) -> int:
        """Get the server port with validation."""
        try:
            return int(os.getenv("SERVER_PORT", "8000"))
        except ValueError:
            return 8000  # Fallback to default
    
    @property
    def health_check_port(self) -> int:
        """Get the health check port with validation."""
        try:
            return int(os.getenv("HEALTH_CHECK_PORT", "8001"))
        except ValueError:
            return 8001  # Fallback to default
    
    @property
    def mcp_master_api_key(self) -> Optional[str]:
        """Get the MCP master API key."""
        return os.getenv("MCP_MASTER_API_KEY")
    
    @property
    def mcp_master_api_key_name(self) -> str:
        """Get the MCP master API key header name."""
        return os.getenv("MCP_MASTER_API_KEY_NAME", "x-api-key")
    
    @property
    def correlation_id_name(self) -> str:
        """Get the correlation ID header name."""
        return os.getenv("CORRELATION_ID_NAME", "x-correlation-id")
    
    @property
    def mcp_base_path(self) -> str:
        """Get the MCP server base path, normalized without leading/trailing slashes."""
        path = os.getenv("MCP_BASE_PATH", "").strip()
        return path.strip("/") if path else ""
    
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary format for backward compatibility.
        
        Returns:
            Dictionary with configuration values
        """
        return {
            "log_level": self.log_level,
            "log_file": self.log_file,
            "server_host": self.server_host,
            "server_port": self.server_port,
            "health_check_port": self.health_check_port,
            "mcp_master_api_key": self.mcp_master_api_key,
            "mcp_master_api_key_name": self.mcp_master_api_key_name,
            "correlation_id_name": self.correlation_id_name,
            "mcp_base_path": self.mcp_base_path,
        }


# Global configuration instance - initialized once
try:
    app_config = Config()
except ValueError as e:
    # Log error and create with defaults if validation fails
    import sys
    print(f"Configuration error: {e}", file=sys.stderr)
    # Create a temporary config that will use defaults
    app_config = object.__new__(Config)


# Legacy function for backward compatibility only
def get_configuration() -> Dict[str, Any]:
    """
    Get configuration dictionary.
    
    Returns:
        Dictionary with configuration values
        
    Note: Deprecated - use app_config directly for new code.
    """
    return app_config.to_dict()


# The following getter functions are deprecated in favor of using app_config directly
# They are kept only for backward compatibility
get_log_level = lambda: app_config.log_level
get_log_file = lambda: app_config.log_file
get_server_host = lambda: app_config.server_host
get_server_port = lambda: app_config.server_port
get_health_check_port = lambda: app_config.health_check_port
get_mcp_master_api_key = lambda: app_config.mcp_master_api_key
get_mcp_master_api_key_name = lambda: app_config.mcp_master_api_key_name
get_correlation_id_name = lambda: app_config.correlation_id_name
get_mcp_base_path = lambda: app_config.mcp_base_path
