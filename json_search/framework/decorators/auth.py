"""API key authentication decorator for MCP server."""

from starlette.status import HTTP_403_FORBIDDEN
from starlette.exceptions import HTTPException
from ..core.context import get_api_key_from_context
from ..core.utils import get_app_logger
from ..core.config import get_mcp_master_api_key, get_mcp_master_api_key_name


def require_api_key(func):
    """
    Decorator to protect a tool with API key authentication.
    
    This decorator checks for an api key in the request context (from the header).
    """
    import functools
    import logging

    @functools.wraps(func)
    async def wrapper(params):
        logger = get_app_logger()
        master_api_key = get_mcp_master_api_key()
        master_api_key_name = get_mcp_master_api_key_name()

        # Check if we should use detailed logging (DEBUG level)
        is_debug_logging = logger.isEnabledFor(logging.DEBUG)

        # Enhanced logging for debugging - only in DEBUG mode
        if is_debug_logging:
            logger.debug(f"=== Authentication Debug for tool '{func.__name__}' ===")
            logger.debug(f"Master API key configured: {'Yes' if master_api_key else 'No'}")
            logger.debug(f"Master API key length: {len(master_api_key) if master_api_key else 0}")

        # If no master API key is configured, log a warning and allow access
        if not master_api_key:
            logger.warning("No MCP_MASTER_API_KEY set. Bypassing authentication.")
            return await func(params)

        # Check for API key in the context (from header)
        api_key_from_header = get_api_key_from_context()
        
        if is_debug_logging:
            logger.debug(f"API key from header: {'Present' if api_key_from_header else 'Missing'}")
        
        if api_key_from_header:
            if is_debug_logging:
                logger.debug(f"Header API key length: {len(api_key_from_header)}")
                logger.debug(f"Header API key suffix: ***{api_key_from_header[-4:] if len(api_key_from_header) > 4 else '***'}")
            
            if api_key_from_header == master_api_key:
                if is_debug_logging:
                    logger.debug("✓ Header API key authentication successful")
                return await func(params)
            else:
                # Log authentication failure - keep warning for security audit
                logger.warning("✗ Invalid API key received")
                if is_debug_logging:
                    logger.debug(f"Invalid API key suffix: ***{api_key_from_header[-4:] if len(api_key_from_header) > 4 else '***'}")
                    logger.debug(f"Expected suffix: ***{master_api_key[-4:] if len(master_api_key) > 4 else '***'}")
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Invalid API key provided in '{master_api_key_name}' header."
                )

        # Log missing API key - keep warning for security audit
        logger.warning("✗ Missing API key. Authentication failed.")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=f"Missing API key. Provide it in the '{master_api_key_name}' header"
        )
    
    return wrapper
