"""Request context management using contextvars."""

import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional
from .utils import get_app_logger
from .config import get_mcp_master_api_key_name, get_correlation_id_name

# Context variable to store request information
request_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar("request_context", default=None)

def get_request_context() -> Optional[Dict[str, Any]]:
    """Get the current request context."""
    return request_context.get()

def set_request_context(context: Dict[str, Any]):
    """Set the request context."""
    request_context.set(context)

def get_api_key_from_context() -> Optional[str]:
    """Get the API key from the current context."""
    # return api_key_context.get()
    context = get_request_context()
    if not context or not context.get("headers"):
        return None

    headers = context.get("headers")

    api_key_name = get_mcp_master_api_key_name()
    if context.get(api_key_name):
        return context[api_key_name]    
    
    api_key_value = None

    for header_name, header_value in headers.items():
        if header_name.lower() == api_key_name.lower():
            api_key_value = header_value
            break

    if api_key_value:
        context[api_key_name] = api_key_value
        get_app_logger().debug(f"🔍 [] API key extracted from headers")
    return api_key_value


def setup_correlation_id(headers: Dict[str, Any]) -> str:
    """
    Setup and return a correlation ID for the current request.
    
    Extracts correlation ID from headers if present, otherwise generates a new one.
    
    Args:
        headers: Request headers dictionary
        
    Returns:
        str: The correlation ID for the current request
    """
    correlation_id_header_name = get_correlation_id_name()
    correlation_id_value = None
    
    # Try to get correlation ID from headers (case-insensitive)
    for header_name, header_value in headers.items():
        if header_name.lower() == correlation_id_header_name.lower():
            correlation_id_value = header_value
            break
    
    # Generate a new correlation ID if not found in headers
    if not correlation_id_value:
        correlation_id_value = str(uuid.uuid4())
    
    return correlation_id_value


def get_correlation_id() -> Optional[str]:
    """
    Get the correlation ID from the current request context.
    
    Returns:
        Optional[str]: The correlation ID if present in context, None otherwise
    """
    context = get_request_context()
    if not context:
        return None
        
    correlation_id_header_name = get_correlation_id_name()
    return context.get(correlation_id_header_name)
