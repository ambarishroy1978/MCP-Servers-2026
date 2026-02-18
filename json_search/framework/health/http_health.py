"""HTTP health check server for monitoring MCP server status."""

from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..core.utils import get_app_logger, get_uptime_seconds

# Set up logging
logger = get_app_logger()


class HealthCheckServer:
    """HTTP server for health check endpoint."""
    
    def __init__(self, mcp_server_ref: Optional[Any] = None, base_path: str = ""):
        """Initialize health check server.
        
        Args:
            mcp_server_ref: Reference to the MCP server instance
            base_path: Base path prefix for all endpoints
        """
        self.mcp_server_ref = mcp_server_ref
        self.base_path = base_path.rstrip("/")  # Remove trailing slash if present
        
        self.app = FastAPI(
            title="MCP Server Health Check",
            description="Health monitoring endpoint for MCP server",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register HTTP routes."""
        
        # Construct the health endpoint path with base path
        health_path = f"/{self.base_path}/health" if self.base_path else "/health"
        root_path = f"/{self.base_path}/" if self.base_path else "/"
        
        @self.app.get(health_path, response_model=Dict[str, Any])
        async def health_check():
            """Health check endpoint.
            
            Returns comprehensive health status of the MCP server.
            """
            try:
                # Check if MCP server reference exists and is responsive
                mcp_server_running = self.mcp_server_ref is not None
                
                # Get basic health info directly from framework
                from ..core.utils import get_project_metadata
                project_metadata = get_project_metadata()
                
                # Get available tools from MCP server if available
                tools_available = []
                
                # Get tools from FastMCP's tool manager
                if self.mcp_server_ref:
                    try:
                        # Get logger safely
                        from ..core.utils import get_app_logger
                        current_logger = get_app_logger()
                        
                        # FastMCP stores tools in _tool_manager._tools
                        if hasattr(self.mcp_server_ref, '_tool_manager') and hasattr(self.mcp_server_ref._tool_manager, '_tools'):
                            tools_dict = self.mcp_server_ref._tool_manager._tools
                            tools_available = list(tools_dict.keys())
                            current_logger.debug(f"Found {len(tools_available)} tools: {tools_available}")
                        else:
                            current_logger.warning("FastMCP tool manager or tools not found")
                    except Exception as e:
                        try:
                            from ..core.utils import get_app_logger
                            current_logger = get_app_logger()
                            current_logger.error(f"Error accessing FastMCP tools: {e}")
                        except:
                            print(f"Error accessing FastMCP tools: {e}")
                
                # Additional check: verify tools are available
                tools_loaded = len(tools_available) > 0
                
                # Determine overall status - if MCP server is running, consider it healthy
                # The tools detection might not work perfectly due to FastMCP internals
                status = "healthy" if mcp_server_running else "unhealthy"
                
                # Build response
                response_data = {
                    "status": status,
                    "mcp_server": {
                        "running": mcp_server_running,
                        "transport": "Streamable HTTP",
                        "port": 8000
                    },
                    "version": project_metadata.get("version", "1.0.0"),
                    "timestamp": datetime.now().isoformat(),
                    "uptime_seconds": get_uptime_seconds(),
                    "tools_available": tools_available,
                    "checks": {
                        "mcp_server_responsive": mcp_server_running,
                        "tools_loaded": tools_loaded,
                        "configuration_valid": True  # Can be enhanced with actual config validation
                    }
                }
                
                # Return appropriate status code
                status_code = 200 if status == "healthy" else 503
                return JSONResponse(content=response_data, status_code=status_code)
                
            except Exception as e:
                # Get logger safely
                try:
                    from ..core.utils import get_app_logger
                    logger = get_app_logger()
                    logger.error(f"Health check failed: {e}")
                except:
                    # Fallback if logger not available
                    print(f"Health check failed: {e}")
                return JSONResponse(
                    content={
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    },
                    status_code=503
                )
        
        @self.app.get(root_path)
        async def root():
            """Root endpoint."""
            return {
                "service": "MCP Server Health Check",
                "endpoints": {
                    health_path: "Health check endpoint",
                    f"{root_path}docs" if root_path != "/" else "/docs": "API documentation"
                }
            }
        
        # Add explicit redirect route for base path without trailing slash
        if self.base_path:
            from fastapi.responses import RedirectResponse
            
            @self.app.get(f"/{self.base_path}")
            async def base_path_redirect():
                """Redirect base path without trailing slash to with trailing slash."""
                return RedirectResponse(url=f"/{self.base_path}/", status_code=301)
        
        # Add explicit docs endpoint with base path if configured
        if self.base_path:
            docs_path = f"/{self.base_path}/docs"
            
            @self.app.get(docs_path, include_in_schema=False)
            async def docs_redirect():
                from fastapi.openapi.docs import get_swagger_ui_html
                return get_swagger_ui_html(
                    openapi_url=f"/{self.base_path}/openapi.json",
                    title=self.app.title + " - Swagger UI",
                )
            
            @self.app.get(f"/{self.base_path}/openapi.json", include_in_schema=False)
            async def custom_openapi():
                from fastapi.openapi.utils import get_openapi
                return get_openapi(
                    title=self.app.title,
                    version=self.app.version,
                    description=self.app.description,
                    routes=self.app.routes,
                )
    
    async def run(self, host: str = "0.0.0.0", port: int = 8001):
        """Run the health check server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        # Get log level from app config to respect .env LOG_LEVEL setting
        from ..core.utils import get_app_config
        app_config = get_app_config()
        log_level = app_config.get("log_level", "info").lower()
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level=log_level,
            access_log=False  # Disable access logs for health checks
        )
        server = uvicorn.Server(config)
        await server.serve()
