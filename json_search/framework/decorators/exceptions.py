"""Exception handling decorator for MCP server tools."""

from ..core.utils import get_app_logger, ValidationError, APIError, ToolExecutionError


def handle_exceptions(tool_name: str):
    """
    Decorator for standardized exception handling in MCP tools.
    
    Args:
        tool_name: Name of the tool for logging purposes
        
    Returns:
        Decorated function with exception handling
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def wrapper(params):
            logger = get_app_logger()
            try:
                # Remove duplicate logging - let log_requests handle tool execution logging
                result = await func(params)
                # Convert Pydantic model to dict if needed
                return result.model_dump() if hasattr(result, 'model_dump') else result
            except ValidationError as e:
                # Only log the error details, not the tool execution
                logger.error(f"Validation error in {tool_name}: {e}")
                return {"error": f"Validation error: {str(e)}"}
            except (APIError, ToolExecutionError) as e:
                error_type = "API error" if isinstance(e, APIError) else "Execution error"
                logger.error(f"{error_type} in {tool_name}: {e}")
                return {"error": f"{error_type}: {str(e)}"}
            except Exception as e:
                logger.error(f"Unexpected error in {tool_name}: {e}")
                return {"error": f"Unexpected error: {str(e)}"}
        return wrapper
    return decorator
