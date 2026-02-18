# Next AI MCP Server - Developer Guide

A production-ready Model Context Protocol (MCP) server implementation with an **ultra-clean design** that automatically discovers and registers your tools. This framework separates infrastructure code from developer customizations, providing built-in authentication, logging, correlation ID tracking, and health monitoring.

## 🚀 Quick Start for Tool Development

This server features an **ultra-clean architecture** with automatic tool discovery. Simply create your domain modules and the framework automatically finds and registers your tools - no manual registration required!

### Framework vs. Developer Code

```
project-root/
├── framework/          # ⚠️  Infrastructure code - DON'T MODIFY
│   ├── core/          # Configuration, context, logging
│   ├── decorators/    # Authentication, logging, error handling
│   ├── middleware/    # HTTP middleware, correlation ID
│   ├── server/        # Server factory and auto-discovery
│   └── health/        # Health check server
├── src/               # ✅ Your domain modules go here
│   ├── sample/        # Example domain with sample tools
│   │   ├── tools.py   # Tool implementations
│   │   ├── server.py  # Tool registrations (auto-discovered)
│   │   └── models.py  # Data models
│   ├── your_domain/   # Create your own domain modules
│   │   ├── tools.py   # Your tool implementations
│   │   ├── server.py  # Your tool registrations
│   │   └── models.py  # Your data models
│   └── custom/        # Additional shared modules
```

### 🎯 Ultra-Clean Design Features

- **🔍 Auto-Discovery**: Framework automatically finds and registers tools from domain modules
- **📦 Domain Organization**: Organize tools by business domain (e.g., `weather/`, `analytics/`, `ai/`)
- **🚀 Zero Configuration**: Just create your domain module and tools are automatically available
- **🔧 Global Registration**: Use `@register_tool("tool_name")` decorator for instant registration
- **📝 Clean Separation**: Framework code vs. domain code clearly separated

## 🛠️ Adding a New Domain & Tools (Ultra-Clean Way)

### Step 0: Environment Setup and Configuration

Before you start developing tools, you need to set up your environment and configure the server:

```bash
# 1. Clone the repository and navigate to the project directory
git clone <repository-url>
cd next-ai-mcp-tools

# 2. Create and activate a Python virtual environment (recommended version 3.12)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Set up environment configuration
cp .env.example .env

# 5. Edit the .env file with your specific configuration
# See .env.example for detailed comments on each variable
# At minimum, set these for production:
# - MCP_MASTER_API_KEY: Your secure API key for authentication
# - LOG_LEVEL: Set to INFO for production, DEBUG for development
# - SERVER_HOST: Set to 0.0.0.0 for production deployment

# 6. Verify your setup by running the server
python run_server.py

# 7. Test the health endpoint
curl http://localhost:8001/{MCP_BASE_PATH}/health
```

**Important Configuration Notes:**
- **Development Mode**: If you don't set `MCP_MASTER_API_KEY`, the server runs in development mode with authentication bypassed
- **Production Mode**: Always set a strong `MCP_MASTER_API_KEY` (minimum 32 characters) for production deployments
- **Logging**: Use `LOG_LEVEL=DEBUG` for development and `LOG_LEVEL=INFO` for production
- **Base Paths**: The `MCP_BASE_PATH` determines your MCP endpoint URLs (default: `/product-a`)

### Step 1: Create Your Domain Module

Create a new domain directory under `src/` (e.g., `src/analytics/`, `src/weather/`, `src/ai/`):

```bash
# Create your domain directory
mkdir src/your_domain
touch src/your_domain/__init__.py
touch src/your_domain/tools.py
touch src/your_domain/server.py  
touch src/your_domain/models.py
```

### Step 2: Define Your Tool Logic (`src/your_domain/tools.py`)

```python
from framework import get_app_logger, ValidationError, ToolExecutionError
from .models import YourToolResult

async def your_custom_tool(param1: str, param2: int = 10) -> YourToolResult:
    """
    Description of what your tool does.
    
    Args:
        param1: Description of required parameter
        param2: Description of optional parameter with default
        
    Returns:
        YourToolResult: Structured response data
        
    Raises:
        ValidationError: If input validation fails
        ToolExecutionError: If tool execution fails
    """
    logger = get_app_logger()
    logger.info(f"Executing your_custom_tool with param1: {param1}")
    
    # Input validation
    if not param1 or not param1.strip():
        raise ValidationError("param1 cannot be empty")
    
    try:
        # Your tool implementation here
        processed_data = param1.upper()  # Example processing
        
        result = YourToolResult(
            input_param=param1,
            processed_value=processed_data,
            count=param2,
            success=True
        )
        
        logger.info("Successfully executed your_custom_tool")
        return result
        
    except Exception as e:
        logger.error(f"Failed to execute your_custom_tool: {e}")
        raise ToolExecutionError(f"Tool execution failed: {e}")
```

### Step 3: Define Your Data Model (`src/your_domain/models.py`)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class YourToolResult(BaseModel):
    """Response model for your_custom_tool."""
    input_param: str = Field(..., description="Original input parameter")
    processed_value: str = Field(..., description="Processed result")
    count: int = Field(..., description="Count value")
    success: bool = Field(..., description="Whether operation succeeded")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_param": "hello world",
                "processed_value": "HELLO WORLD",
                "count": 10,
                "success": True,
                "timestamp": "2025-01-03T12:00:00Z",
                "metadata": {"processing_time": 0.001}
            }
        }
```

### Step 4: Register Your Tool (`src/your_domain/server.py`)

```python
"""Your domain tool registrations."""

from typing import Any, Dict
from pydantic import BaseModel, Field
from framework import register_tool

from .tools import your_custom_tool
from .models import YourToolResult

# Define parameter model
class YourToolParams(BaseModel):
    """Parameters for your_custom_tool."""
    param1: str = Field(..., description="Required string parameter")
    param2: int = Field(10, description="Optional integer parameter with default")

# Register the tool - Framework auto-discovers this!
@register_tool("your_custom_tool")
async def your_custom_tool_wrapper(params: YourToolParams) -> Dict[str, Any]:
    """
    Brief description for MCP clients.
    
    Detailed description of what the tool does, how to use it,
    and what kind of results to expect.
    """
    result = await your_custom_tool(
        param1=params.param1,
        param2=params.param2
    )
    return result.model_dump()
```

**✨ Ultra-Clean Magic**: The `@register_tool("tool_name")` decorator automatically:
- Registers with the global MCP server instance
- Applies authentication, logging, and error handling
- Makes your tool instantly available to MCP clients
- No manual server configuration required!

### Step 5: Test Your Tool (Auto-Discovery in Action!)

```bash
# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the server - it automatically discovers your domain!
python run_server.py

# Your tool is instantly available! The server will log:
# "Auto-discovered domain: your_domain"
# "Registered tool: your_custom_tool"

# Test your tool using an MCP client
# The server exposes MCP protocol endpoints:
# - Streamable HTTP endpoint: http://localhost:8000/product-a/mcp/

# Use MCP clients like:
# - Intelligence Studio MCP Connection
# - MCP Inspector: npx @modelcontextprotocol/inspector
# - Custom MCP client applications
```

### 🎉 That's It! Ultra-Clean Development

Your tool is now automatically:
- ✅ **Discovered** by the framework
- ✅ **Registered** with the MCP server
- ✅ **Available** to MCP clients
- ✅ **Protected** with authentication
- ✅ **Logged** with correlation IDs
- ✅ **Monitored** for health checks

**No configuration files, no manual registration, no boilerplate!**

## 🎯 Ultra-Clean Framework Features (Automatic)

When you create a domain module with tools, the framework automatically provides:

### 🔍 Auto-Discovery
- Scans `src/` directory for domain modules
- Automatically imports and registers tools
- No manual configuration required
- Instant tool availability

### 🌐 Global Server Instance
- Single MCP server instance shared across domains
- Tools register with `@register_tool("name")` decorator
- No need to pass server instances around
- Clean, simple registration pattern

### ✅ Authentication
- API key validation via HTTP headers
- Development mode (no auth) vs production mode
- Configurable API key header names

### ✅ Logging & Tracing
- Request/response logging with correlation IDs
- Performance metrics (execution time)
- Debug vs production logging levels
- Automatic log correlation across components

### ✅ Error Handling
- Comprehensive exception handling
- Sanitized error responses
- Detailed error logging with correlation IDs
- Custom exception types

### ✅ Input/Output Validation
- Pydantic model validation
- Type safety and conversion
- Structured error messages
- JSON schema generation

### ✅ Health Monitoring
- Health check endpoints
- Server status monitoring
- Tool availability tracking
- Production-ready monitoring

## 📋 Configuration

Configure your server using environment variables (`.env` file):

```bash
# Authentication
MCP_MASTER_API_KEY=your-secret-key-here
MCP_MASTER_API_KEY_NAME=x-api-key

# Correlation ID Tracking
CORRELATION_ID_NAME=x-correlation-id

# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=8000
HEALTH_CHECK_PORT=8001

# Base Path Configuration
MCP_BASE_PATH=/product-a/mcp/v1

# Logging
LOG_LEVEL=INFO
LOG_FILE=

```

## 🔧 Development Modes

### Development Mode (Default)
When no `MCP_MASTER_API_KEY` is set, the server runs in development mode:
- Authentication is bypassed for easier testing
- Debug logging is recommended (`LOG_LEVEL=DEBUG`)
- Server accessible only from localhost by default

```bash
# Run in development mode
LOG_LEVEL=DEBUG python run_server.py
```

### Production Mode
For production deployments, configure authentication and security:
- Set a strong `MCP_MASTER_API_KEY` (minimum 32 characters)
- Use `LOG_LEVEL=INFO` for production logging
- Set `SERVER_HOST=0.0.0.0` for network accessibility

```bash
# Production configuration
MCP_MASTER_API_KEY=strong-cryptographic-key-32-chars-min
LOG_LEVEL=INFO
SERVER_HOST=0.0.0.0
python run_server.py
```

## 🏗️ Architecture Overview

### Framework Components (Don't Modify)
- **`framework/core/`**: Configuration, context management, logging
- **`framework/decorators/`**: Authentication, logging, error handling decorators
- **`framework/middleware/`**: HTTP middleware for request processing
- **`framework/server/`**: Server factory, auto-discovery, and tool registration
- **`framework/health/`**: Health check server and endpoints

### Developer Components (Your Domain Modules)
- **`src/sample/`**: Example domain with sample tools (reference implementation)
- **`src/your_domain/`**: Your domain modules organized by business area
  - **`tools.py`**: Tool implementations for this domain
  - **`server.py`**: Tool registrations (auto-discovered by framework)
  - **`models.py`**: Pydantic models for your domain's data structures
- **`src/custom/`**: Shared utilities and custom modules across domains

## 🔍 Built-in Sample Domain

The server includes a complete sample domain (`src/sample/`) with three tools to demonstrate the ultra-clean patterns:

### Sample Domain Structure
```
src/sample/
├── __init__.py
├── tools.py      # Tool implementations
├── server.py     # Tool registrations (auto-discovered!)
└── models.py     # Data models
```

### 1. Weather Tool
```python
# Usage example
{
  "location": "London"
}
# Returns weather data with temperature, humidity, etc.
```

### 2. Statistics Tool
```python
# Usage example
{
  "numbers": [1, 2, 3, 4, 5]
}
# Returns statistical analysis (mean, median, std dev, etc.)
```

### 3. Text Analysis Tool
```python
# Usage example
{
  "text": "Hello world! This is a test.",
  "top_words": 5
}
# Returns word count, character count, most common words, etc.
```

**🎯 Study the Sample**: The `src/sample/` domain shows the complete ultra-clean pattern for organizing and registering tools.

## 🚦 Health Monitoring

The server includes a dedicated health check server:

```bash
# Check server health
curl http://localhost:8001/product-a/health

# Response includes:
{
  "status": "healthy",
  "mcp_server": {"running": true, "transport": "Streamable HTTP", "port": 8000},
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "tools_available": ["get_weather", "calculate_statistics", "analyze_text"],
  "checks": {
    "mcp_server_responsive": true,
    "tools_loaded": true,
    "configuration_valid": true
  }
}
```

## 🔐 Authentication Methods

### MCP Client Authentication
MCP tools are accessed through MCP clients (like Claude Desktop) that handle authentication automatically using the configured API key. The server validates requests using:

- **API Key Header**: Configurable header name (default: `X-API-Key`)
- **Development Mode**: If no `MCP_MASTER_API_KEY` is configured, authentication is bypassed for easier local development

### Development Mode
If no `MCP_MASTER_API_KEY` is configured, the server runs in development mode with authentication bypassed (useful for local development).

## 📊 Correlation ID Tracking

The server automatically tracks requests with correlation IDs for debugging and monitoring:

### Automatic Features
- Extracts correlation ID from `X-Correlation-ID` header (configurable)
- Generates UUID if no correlation ID provided
- Includes correlation ID in all log entries
- Propagates correlation ID throughout request lifecycle

### MCP Client Integration
MCP clients can include correlation IDs in their requests for request tracing. All logs for a request will include the correlation ID for easy debugging.

## 🧪 Testing Your Tools

### Manual Testing
```bash
# Test individual tools from any domain
python -c "
import asyncio
from src.your_domain.tools import your_custom_tool
result = asyncio.run(your_custom_tool('test', 5))
print(result)
"

# Test sample domain tools
python -c "
import asyncio
from src.sample.tools import get_weather
result = asyncio.run(get_weather('London'))
print(result)
"
```

## 🤖 Sample Cline Prompt for Adding New Domains & Tools

When working with Cline (or other AI assistants) to add new domains and tools to this ultra-clean MCP server, use this sample prompt template:

```
I need to add a new domain with MCP tools to this Next AI MCP Server project. Here's what I want to build:

**Domain Name**: [your_domain] (e.g., analytics, weather, ai, etc.)
**Tool Name**: [your_tool_name]
**Purpose**: [Brief description of what the tool should do]
**Input Parameters**: 
- [param1]: [type] - [description] (required/optional)
- [param2]: [type] - [description] (required/optional)
**Expected Output**: [Description of what the tool should return]

**Specific Requirements**:
- [Any specific business logic requirements]
- [External APIs to integrate with, if any]
- [Validation rules for inputs]
- [Error handling requirements]

Please follow the ultra-clean framework patterns in this project:

1. **Ultra-Clean Architecture**: This project uses auto-discovery - create domain modules and tools are automatically registered
2. **Domain Structure**: 
   - Create `src/[domain_name]/` directory
   - Add tool logic to `src/[domain_name]/tools.py`
   - Define data models in `src/[domain_name]/models.py` 
   - Register tools in `src/[domain_name]/server.py` using `@register_tool("name")`
   - Add comprehensive test cases to `tests/test_server.py`
3. **Auto-Discovery**: The framework automatically finds and registers your domain - no manual configuration needed
4. **Code Style**: Follow the existing patterns in the sample domain (`src/sample/`)

**Example of existing domain structure** (for reference):
- Study `src/sample/` for the complete ultra-clean pattern
- Tool functions in `tools.py` with proper error handling and logging
- Pydantic models in `models.py` for structured responses
- Registration in `server.py` with `@register_tool("tool_name")` decorator
- Test classes with comprehensive test coverage

Please implement the complete domain with tools including all test cases following the ultra-clean patterns, and let me know when it's ready for testing.
```

### Example Usage with Cline

Here's a concrete example of how to use the ultra-clean prompt:

```
I need to add a new domain with MCP tools to this Next AI MCP Server project. Here's what I want to build:

**Domain Name**: web_analysis
**Tool Name**: url_analyzer
**Purpose**: Analyze a URL to extract metadata like title, description, status code, and response time
**Input Parameters**: 
- url: str - The URL to analyze (required)
- timeout: int - Request timeout in seconds (optional, default: 10)
- include_headers: bool - Whether to include response headers (optional, default: false)
**Expected Output**: URL metadata including title, description, status code, response time, and optionally headers

**Specific Requirements**:
- Validate URL format before making requests
- Handle HTTP errors gracefully (404, 500, etc.)
- Extract HTML meta tags (title, description, keywords)
- Measure response time
- Support both HTTP and HTTPS URLs
- Return structured data with clear success/error indicators

Please follow the ultra-clean framework patterns in this project:

1. **Ultra-Clean Architecture**: This project uses auto-discovery - create domain modules and tools are automatically registered
2. **Domain Structure**: 
   - Create `src/web_analysis/` directory
   - Add tool logic to `src/web_analysis/tools.py`
   - Define data models in `src/web_analysis/models.py` 
   - Register tools in `src/web_analysis/server.py` using `@register_tool("url_analyzer")`
   - Add comprehensive test cases to `tests/test_server.py` using sample url https://www.google.com
3. **Auto-Discovery**: The framework automatically finds and registers your domain - no manual configuration needed
4. **Code Style**: Follow the existing patterns in the sample domain (`src/sample/`)

Please implement the complete domain with tools following the ultra-clean patterns, and let me know when it's ready for testing.
```

This prompt template provides Cline with:
- **Clear requirements** for the specific domain and tools you want to build
- **Ultra-clean architecture context** so it understands the auto-discovery system
- **Domain organization guidance** following the established patterns
- **Reference to sample domain** for consistency and best practices

## 🐛 Debugging Tips

### Enable Debug Logging
```bash
LOG_LEVEL=DEBUG python run_server.py
```

### Check Correlation IDs
Look for correlation IDs in logs to trace specific requests:
```
2025-01-03 12:00:00 - [abc-123-def] - INFO - 🔧 Executing tool: your_custom_tool
2025-01-03 12:00:01 - [abc-123-def] - INFO - ✅ Tool completed successfully in 0.123s
```

### Common Issues
1. **Import Errors**: Ensure you're importing from `framework` package
2. **Authentication Errors**: Check `MCP_MASTER_API_KEY` configuration
3. **Validation Errors**: Verify your Pydantic models are correct
4. **Tool Not Found**: Ensure tool is registered in `src/server.py`

## 🔧 Advanced Patterns

### External API Integration
```python
import httpx
from framework import APIError

async def tool_with_api_call(query: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://api.example.com/search?q={query}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise APIError(f"External API failed: {e}")
```

### Custom Validation
```python
from pydantic import validator

class CustomParams(BaseModel):
    email: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```



## 📚 Framework API Reference

### Available Imports
```python
from framework import (
    # Exceptions
    ValidationError,
    ToolExecutionError,
    APIError,
    MCPServerError,
    
    # Utilities
    get_app_logger,
    get_app_config,
    
    # Server factory
    create_mcp_server,
    register_tool,
    
    # Decorators (used in server.py)
    require_api_key,
    log_requests,
    handle_exceptions,
    
    # Configuration helpers
    get_log_level,
    get_server_host,
    get_server_port,
    get_correlation_id_name,
)
```

### Decorator Usage
```python
# In src/server.py - decorators are applied in this order:
@mcp.tool()                    # FastMCP registration
@log_requests                  # Request/response logging
@require_api_key              # Authentication
@handle_exceptions("tool_name") # Error handling
async def your_tool_wrapper(params: YourParams):
    # Your tool logic
    pass
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Production configuration
MCP_MASTER_API_KEY=strong-cryptographic-key-32-chars-min
LOG_LEVEL=INFO
LOG_FILE=/var/log/mcp-server/server.log
SERVER_HOST=0.0.0.0
HEALTH_CHECK_PORT=8001
```

### Docker Deployment
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000 8001
CMD ["python", "run_server.py"]
```

### Health Check Integration
```yaml
# Docker Compose health check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 🤝 Contributing

### Adding Framework Features
If you need to modify framework code:
1. Understand the impact on existing tools
2. Maintain backward compatibility
3. Update framework exports in `framework/__init__.py`
4. Add comprehensive tests
5. Update documentation

### Best Practices
1. **Keep business logic in `src/`** - Don't modify framework files
2. **Use framework APIs** - Import from `framework` package
3. **Follow naming conventions** - Use descriptive names for tools and models
4. **Add proper error handling** - Use framework exceptions
5. **Document your tools** - Add comprehensive docstrings
6. **Test thoroughly** - Test both success and error cases

## 📖 Additional Resources

- **Architecture Documentation**: See `ARCHITECTURE.md` for detailed technical architecture
- **Framework Structure**: See `FRAMEWORK_STRUCTURE.md` for framework organization
- **Sample Tools**: Examine `src/tools.py` for implementation patterns
- **Configuration**: Check `.env.example` for all available options

## 🆘 Troubleshooting

### Framework Import Issues
```python
# ❌ Wrong - don't import from framework internals
from framework.core.utils import get_app_logger

# ✅ Correct - import from framework package
from framework import get_app_logger
```

### Domain Organization Issues
```python
# ❌ Wrong - mixing domains or putting tools in wrong places
from src.sample.tools import your_custom_tool  # Don't mix domains

# ✅ Correct - organize by domain
from src.your_domain.tools import your_custom_tool
from src.sample.tools import get_weather  # Sample tools stay in sample
```

### Auto-Discovery Not Working
1. **Check domain structure**: Ensure you have `src/domain_name/server.py`
2. **Verify `@register_tool` usage**: Use `@register_tool("tool_name")` decorator
3. **Check imports**: Ensure your domain's `server.py` imports tool functions
4. **Review server logs**: Look for "Auto-discovered domain: your_domain" messages
5. **Restart server**: Auto-discovery happens at startup

### Authentication Issues
```bash
# Check if development mode is active
grep MCP_MASTER_API_KEY .env

# If empty or missing, server runs in development mode (no auth required)
# For production, set a strong API key
```

### Correlation ID Not Appearing
```bash
# Ensure you're using the correct header name
curl -H "X-Correlation-ID: test-123" ...

# Check configuration
echo $CORRELATION_ID_NAME  # Should show header name (default: x-correlation-id)
```

### Tool Not Registering
1. Check that tool function is imported in `src/server.py`
2. Verify decorator order is correct
3. Ensure parameter model is properly defined
4. Check server logs for registration errors

---

**Ready to build your ultra-clean MCP server?** 

1. **Study the sample**: Examine `src/sample/` to understand the pattern
2. **Create your domain**: Make `src/your_domain/` with the same structure  
3. **Add your tools**: Implement in `tools.py`, register in `server.py`
4. **Run the server**: Auto-discovery handles the rest!

**🚀 Ultra-clean development - no configuration, just code!**
