"""Request logging decorator for MCP server."""

import json
import logging
import time
from typing import Any, Dict, Optional
from functools import wraps

from ..core.context import get_request_context, set_request_context
from ..core.utils import get_app_logger
from ..core.config import get_mcp_master_api_key_name

def log_request_details(
    method: str = "UNKNOWN",
    path: str = "UNKNOWN",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[str] = None
):
    """
    Log detailed request information for debugging.
    
    Args:
        method: HTTP method
        path: Request path
        headers: Request headers
        params: Request parameters
        body: Request body
    """
    logger = get_app_logger()
    # Note: correlation_id is now automatically added by the enhanced formatter
    
    logger.debug("🔍 === INCOMING REQUEST ===")
    logger.debug(f"🔍 Method: {method}")
    logger.debug(f"🔍 Path: {path}")
    
    # Log headers (sanitize sensitive information)
    if headers:
        sanitized_headers = {}
        api_key_header_name = get_mcp_master_api_key_name().lower()
        for key, value in headers.items():
            if key.lower() in ['authorization', api_key_header_name, 'cookie']:
                # Show only the last 4 characters for security
                sanitized_headers[key] = f"***{value[-4:] if len(value) > 4 else '***'}"
            else:
                sanitized_headers[key] = value
        logger.debug(f"🔍 Headers: {json.dumps(sanitized_headers, indent=2)}")
    else:
        logger.debug("🔍 Headers: None")
    
    # Log parameters
    if params:
        # Sanitize API keys in parameters
        logger.debug(f"🔍 Parameters: {json.dumps(params, indent=2)}")
    else:
        logger.debug("🔍 Parameters: None")
    
    # Log body (truncated if too long)
    if body:
        if len(body) > 1000:
            truncated_body = body[:1000] + "... (truncated)"
        else:
            truncated_body = body
        logger.debug(f"🔍 Body: {truncated_body}")
    else:
        logger.debug("🔍 Body: None")
    
    logger.debug("🔍 === END REQUEST LOG ===")

def log_response_details(
    response: Any,
    status_code: int = 200,
    processing_time: Optional[float] = None
):
    """
    Log response details.
    
    Args:
        response: Response data
        status_code: HTTP status code
        processing_time: Time taken to process request
    """
    logger = get_app_logger()
    # Note: correlation_id is now automatically added by the enhanced formatter
    
    logger.debug("📤 === RESPONSE ===")
    logger.debug(f"📤 Status: {status_code}")
    
    if processing_time:
        logger.debug(f"📤 Processing time: {processing_time:.3f}s")
    
    # Log response (truncated if too long)
    if response:
        response_str = json.dumps(response, indent=2, default=str)
        if len(response_str) > 1000:
            truncated_response = response_str[:1000] + "... (truncated)"
        else:
            truncated_response = response_str
        logger.debug(f"📤 Response: {truncated_response}")
    else:
        logger.debug("📤 Response: None")
    
    logger.debug("📤 === END RESPONSE LOG ===")

def log_requests(func):
    """
    Decorator to add request logging to MCP tool functions.
    
    This decorator logs the incoming request details before processing
    and the response details after processing. It optimizes performance
    by using different logging levels based on the current log level.
    """
    @wraps(func)
    async def wrapper(params):
        
        start_time = time.time()
        logger = get_app_logger()
        
        # Check if we should use detailed logging (DEBUG level)
        is_debug_logging = logger.isEnabledFor(logging.DEBUG)
        
        http_context = get_request_context()

        # Log based on level
        if is_debug_logging:
            # Full detailed logging for DEBUG level
            log_request_details(
                method="MCP_TOOL",
                path=f"/tool/{func.__name__}",
                headers=dict(http_context.get('headers', {})) if http_context else {},
                params=params.model_dump() if hasattr(params, 'model_dump') else {"raw": str(params)}
            )
        else:
            # Simplified logging for INFO and above - correlation_id added automatically by formatter
            logger.info(f"🔧 Executing tool: {func.__name__}")
        
        try:
            # Call the original function
            result = await func(params)
            
            # Log successful response
            processing_time = time.time() - start_time
            
            if is_debug_logging:
                # Full detailed response logging for DEBUG level
                log_response_details(
                    response=result,
                    status_code=200,
                    processing_time=processing_time
                )
            else:
                # Simplified success logging for INFO and above - correlation_id added automatically by formatter
                logger.info(f"✅ Tool {func.__name__} completed successfully in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            # Log timing and basic error info, let handle_exceptions decorator handle detailed error logging
            processing_time = time.time() - start_time
            
            if is_debug_logging:
                # Full detailed error logging for DEBUG level
                error_response = {
                    "error": str(e),
                    "type": type(e).__name__
                }
                log_response_details(
                    response=error_response,
                    status_code=500,
                    processing_time=processing_time
                )
            else:
                # Simplified timing info for INFO and above - correlation_id added automatically by formatter
                logger.info(f"⏱️ Tool {func.__name__} processing time: {processing_time:.3f}s")
            
            # Re-raise the exception for handle_exceptions decorator to process
            raise
    
    return wrapper
