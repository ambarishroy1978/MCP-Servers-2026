import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import URL
from starlette.responses import JSONResponse
from ..core.context import set_request_context, setup_correlation_id
from ..core.config import get_correlation_id_name, get_mcp_base_path
from ..core.utils import get_app_logger


class HeaderCaptureMiddleware(BaseHTTPMiddleware):
    """
    Middleware to capture request headers and set up correlation ID context.
    
    This middleware ensures that each request gets a unique correlation ID
    that persists throughout the request lifecycle.
    
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and set up correlation ID context.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next handler
        """
        headers = dict(request.headers)
        
        # Setup correlation ID from headers or generate new one
        correlation_id = setup_correlation_id(headers)
        
        # Create comprehensive request context
        context = {
            get_correlation_id_name(): correlation_id,
            'method': request.method,
            'url': str(request.url),
            'headers': headers,
            'client': request.client.host if request.client else None,
            'timestamp': time.time(),
        }
        
        # Set the request context for this request
        set_request_context(context)
        
        try:
            # Process the request
            response = await call_next(request)
            return response
            
        except Exception as e:
            # For SSE endpoints, skip error logging to avoid potential ASGI conflicts
            # if self._is_sse_endpoint(request):
            #     raise
                
            # Log error with correlation ID (only for unexpected errors on regular endpoints)
            logger = get_app_logger()
            if logger:
                processing_time = time.time() - context['timestamp']
                logger.error(f"❌ Request failed after {processing_time:.3f}s: {str(e)}")
            raise

class PathPrefixMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle path prefixing for MCP servers.
    
    This middleware strips the configured base path from incoming requests
    to allow standard FastMCP to work with custom base paths.
    """
    
    def __init__(self, app, base_path: str = ""):
        super().__init__(app)
        self.base_path = f"/{base_path.strip('/')}" if base_path else ""
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and handle path prefix stripping.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next handler
        """
        # If base path is configured, block access to root MCP endpoints
        if self.base_path:
            # Block direct access to /mcp when base path is configured
            if request.url.path.startswith('/mcp'):
                return JSONResponse(
                    content={
                        "error": "Not Found",
                        "message": f"MCP endpoint is available at {self.base_path}/mcp",
                        "detail": "Direct access to /mcp is disabled when MCP_BASE_PATH is configured"
                    },
                    status_code=404
                )
            
            # Process requests with the correct base path
            if request.url.path.startswith(self.base_path):
                # Create a new URL with the base path stripped
                path = request.url.path[len(self.base_path):]
                if not path.startswith('/'):
                    path = '/' + path
                
                # Create a new URL with the modified path
                request._url = URL(
                    scheme=request.url.scheme,
                    netloc=request.url.netloc,
                    path=path,
                    query=request.url.query,
                    fragment=request.url.fragment
                )
                
                # Update the scope path and raw_path
                request.scope["path"] = path
                request.scope["raw_path"] = path.encode()
        
        response = await call_next(request)
        return response
