# Next AI MCP Server - Architecture

## Executive Summary

The Next AI MCP Server is a production-ready Model Context Protocol (MCP) server built with Python 3.12 and FastMCP. It demonstrates a framework-based architecture with clear separation between infrastructure and business logic.

### Key Features
- **Framework-Based Architecture**: Separation between framework code (`framework/`) and developer code (`src/`)
- **Streamable HTTP Transport**: Real-time communication via Streamable HTTP protocol
- **API Key Authentication**: Configurable authentication with HTTP headers
- **Request Tracing**: Correlation ID tracking for debugging and monitoring
- **Health Monitoring**: Dedicated health check server
- **Type Safety**: Pydantic validation throughout
- **Sample Tools**: Weather data, statistics, and text processing

### Technology Stack
- **Runtime**: Python 3.12+
- **Framework**: FastMCP (MCP protocol implementation)
- **Transport**: Streamable HTTP (SSE deprecated)
- **Validation**: Pydantic v2
- **HTTP Client**: httpx (async)
- **Configuration**: Environment variables

---

## System Architecture

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#ff6b6b','primaryTextColor':'#ffffff','primaryBorderColor':'#ff6b6b','lineColor':'#ffffff','sectionBkgColor':'#2d3748','altSectionBkgColor':'#4a5568','gridColor':'#718096','secondaryColor':'#4299e1','tertiaryColor':'#38b2ac'}}}%%
graph TB
    subgraph "External"
        CLIENT[MCP Client]
        API[External APIs]
        MONITOR[Monitoring]
    end
    
    subgraph "Next AI MCP Server"
        subgraph "Transport"
            HTTP[Streamable HTTP Transport]
            MIDDLEWARE[HTTP Middleware]
        end
        
        subgraph "Framework"
            AUTH[Authentication]
            CONTEXT[Request Context]
            LOGGING[Logging]
            HEALTH[Health Checks]
        end
        
        subgraph "Application"
            SERVER[Tool Registration]
            TOOLS[Tool Logic]
            MODELS[Data Models]
        end
    end
    
    CLIENT --> HTTP
    HTTP --> MIDDLEWARE
    MIDDLEWARE --> AUTH
    AUTH --> SERVER
    SERVER --> TOOLS
    TOOLS --> API
    MONITOR --> HEALTH
    
    classDef external fill:#4a5568,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef transport fill:#2d3748,stroke:#4299e1,stroke-width:2px,color:#ffffff
    classDef framework fill:#2d3748,stroke:#38b2ac,stroke-width:2px,color:#ffffff
    classDef application fill:#2d3748,stroke:#ff6b6b,stroke-width:2px,color:#ffffff
    
    class CLIENT,API,MONITOR external
    class HTTP,MIDDLEWARE transport
    class AUTH,CONTEXT,LOGGING,HEALTH framework
    class SERVER,TOOLS,MODELS application
```

### Architectural Principles

1. **Framework Separation**: Infrastructure code separate from business logic
2. **Type Safety**: Comprehensive Pydantic validation
3. **Async-First**: Non-blocking operations throughout
4. **Request Tracing**: Correlation ID tracking for observability
5. **Configuration Management**: Environment-based configuration

---

## Framework Structure

The server separates stable infrastructure code from customizable application code:

```
framework/                  # Infrastructure (rarely changes)
├── core/                  # Configuration, context, logging
├── decorators/            # Authentication, logging, error handling
├── middleware/            # HTTP request processing
├── server/                # Server factory and tool registration
└── health/               # Health check server

src/                       # Application code (developer focus)
├── server.py             # Tool registration
├── tools.py              # Business logic
├── models.py             # Data models
└── custom/               # Additional custom modules
```

### Framework Benefits

- **Developer Focus**: Only modify files in `src/` directory
- **Automatic Features**: Authentication, logging, error handling provided
- **Consistency**: Uniform patterns across all tools
- **Extensibility**: Easy to add new tools

---

## Core Components

### Application Layer (`src/`)
- **server.py**: Tool registration with FastMCP and decorator application
- **tools.py**: Business logic implementation with external API integration
- **models.py**: Pydantic data models for validation and type safety

### Framework Layer (`framework/`)
- **decorators/**: Cross-cutting concerns (`@require_api_key`, `@log_requests`, `@handle_exceptions`)
- **middleware/**: HTTP request processing and correlation ID management
- **server/**: Server factory and tool registration utilities (`create_mcp_server`, `register_tool`)
- **core/**: Configuration, context management, and logging infrastructure
- **health/**: Health monitoring with dedicated HTTP server

---

## Data Flow

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#4299e1','primaryTextColor':'#ffffff','primaryBorderColor':'#4299e1','lineColor':'#ffffff','actorBkg':'#2d3748','actorBorder':'#4299e1','actorTextColor':'#ffffff','signalColor':'#ffffff','signalTextColor':'#ffffff','labelBoxBkgColor':'#2d3748','labelBoxBorderColor':'#4299e1','labelTextColor':'#ffffff','loopTextColor':'#ffffff','noteBkgColor':'#4a5568','noteBorderColor':'#38b2ac','noteTextColor':'#ffffff'}}}%%
sequenceDiagram
    participant Client
    participant Middleware
    participant Server
    participant Tool
    participant API
    
    Client->>+Middleware: HTTP Request + Headers
    Note over Middleware: Extract/Generate<br/>Correlation ID
    Middleware->>Middleware: Setup Correlation ID
    Middleware->>+Server: Route to Tool
    Note over Server: Apply Decorators:<br/>Auth, Logging, Validation
    Server->>Server: Validate Input
    Server->>+Tool: Execute Business Logic
    Note over Tool: Process Request<br/>with Business Logic
    Tool->>+API: External API Call
    API-->>-Tool: API Response
    Tool-->>-Server: Tool Result
    Note over Server: Format Response<br/>Log Completion
    Server-->>-Middleware: MCP Response
    Middleware-->>-Client: HTTP Response
```

---

## Error Handling

### Exception Hierarchy

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#ff6b6b','primaryTextColor':'#ffffff','primaryBorderColor':'#ff6b6b','lineColor':'#ffffff','classText':'#ffffff','classBkg':'#2d3748','classBorder':'#4299e1','relationColor':'#ffffff','relationLabelColor':'#ffffff','relationLabelBackground':'#2d3748'}}}%%
classDiagram
    class MCPServerError {
        +message: str
        +correlation_id: str
        +timestamp: datetime
        +__init__(message, correlation_id)
        +to_dict() dict
    }
    
    class ValidationError {
        +field: str
        +constraint: str
        +value: Any
        +get_error_details() dict
    }
    
    class APIError {
        +status_code: int
        +endpoint: str
        +response_body: str
        +is_client_error() bool
        +is_server_error() bool
    }
    
    class ToolExecutionError {
        +tool_name: str
        +operation: str
        +original_error: Exception
        +get_context() dict
    }
    
    MCPServerError <|-- ValidationError : inherits
    MCPServerError <|-- APIError : inherits
    MCPServerError <|-- ToolExecutionError : inherits
    
    note for MCPServerError "Base exception class with\ncorrelation ID tracking"
    note for ValidationError "Input validation failures\nwith field-level details"
    note for APIError "External API call failures\nwith HTTP status context"
    note for ToolExecutionError "Tool execution failures\nwith operation context"
```

### Error Features
- **Structured Exceptions**: Custom hierarchy with correlation ID tracking
- **Automatic Logging**: All errors logged with request context
- **Error Sanitization**: Safe error messages to prevent information leakage

---

## Deployment

### Runtime Requirements
- **Python 3.12+** with virtual environment
- **Environment Variables** for configuration
- **Streamable HTTP Server** for MCP protocol communication
- **Health Check Server** for monitoring

### Configuration
Configuration sources (priority order):
1. Environment variables
2. `.env` file
3. Framework defaults

Key settings:
- **Server**: Host, port, transport
- **Authentication**: API key configuration
- **Logging**: Levels and output destinations
- **Health**: Monitoring endpoints

---

## Security

### Security Features
- **API Key Authentication**: Environment-based with configurable headers
- **Input Validation**: Comprehensive Pydantic validation
- **Request Tracing**: Correlation ID tracking for audit trails
- **Error Sanitization**: Prevent information leakage
- **Context Isolation**: Thread-safe request management

### Security Patterns
- **Validation-First**: All inputs validated before processing
- **Fail-Safe Defaults**: Secure configuration defaults
- **Audit Trail**: Complete request tracing

---

## Adding New Tools

### Development Steps
1. **Define Logic**: Add async function in `src/tools.py`
2. **Create Models**: Add Pydantic models in `src/models.py`
3. **Register Tool**: Add registration in `src/server.py`

### Automatic Features
New tools automatically receive:
- **Authentication** via `@require_api_key` decorator
- **Logging** with correlation ID tracking
- **Error Handling** with structured exceptions
- **Input Validation** through Pydantic models

### Example Tool Pattern
```python
# src/tools.py
async def my_tool(input_param: str) -> MyToolResponse:
    """Business logic implementation."""
    logger = get_app_logger()
    logger.info(f"Processing: {input_param}")
    
    # Your business logic here
    result = process_data(input_param)
    
    return MyToolResponse(result=result)

# src/models.py
class MyToolParams(BaseModel):
    input_param: str = Field(..., description="Input parameter")

class MyToolResponse(BaseModel):
    result: str = Field(..., description="Tool result")

# src/server.py
@register_tool(server, "my_tool")
async def my_tool_wrapper(params: MyToolParams) -> Dict[str, Any]:
    """My custom tool description."""
    result = await my_tool(params.input_param)
    return result.model_dump()
```

This architecture provides a solid foundation for building scalable MCP servers with clear separation of concerns, comprehensive error handling, and production-ready features.
