# Docker Deployment Guide

This guide explains how to containerize and run the Next AI MCP Server using Docker.

## Files Overview

- `Dockerfile` - Multi-stage Docker image definition
- `docker-compose.yml` - Docker Compose configuration for easy deployment
- `.dockerignore` - Files to exclude from Docker build context
- `DOCKER.md` - This documentation file

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and run the container:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Using Docker Commands

1. **Build the image:**
   ```bash
   docker build -t json-helper-mcp-server .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name json-helper-mcp-server \
     -p 8000:8000 \
     -p 8001:8001 \
     -e LOG_LEVEL=INFO \
     json-helper-mcp-server
   ```

3. **View logs:**
   ```bash
   docker logs -f json-helper-mcp-server
   ```

4. **Stop and remove container:**
   ```bash
   docker stop json-helper-mcp-server
   docker rm json-helper-mcp-server
   ```

## Configuration

### Environment Variables

The container supports the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `8000` | MCP server port |
| `HEALTH_CHECK_PORT` | `8001` | Health check server port |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FILE` | `` | Optional log file path |

### Using Environment File

1. **Create a `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your configuration:**
   ```env
   LOG_LEVEL=DEBUG
   ```

3. **Run with Docker Compose (automatically loads .env):**
   ```bash
   docker-compose up --build
   ```

## Ports

The container exposes two ports:

- **8000**: MCP Server (Streamable HTTP transport)
- **8001**: Health Check HTTP endpoint

## Health Check

The container includes a built-in health check that:
- Checks every 30 seconds
- Times out after 10 seconds
- Retries 3 times before marking as unhealthy
- Has a 10-second startup grace period

**Manual health check:**
```bash
curl http://localhost:8001/health
```

## Volumes

### Log Persistence (Optional)

To persist logs outside the container:

```bash
# Create logs directory
mkdir -p ./logs

# Run with volume mount
docker-compose up --build
```

The docker-compose.yml already includes the volume mount for `./logs:/app/logs`.

### Custom Configuration

To use a custom configuration file:

```bash
docker run -d \
  --name json-helper-mcp-server \
  -p 8000:8000 \
  -p 8001:8001 \
  -v $(pwd)/custom.env:/app/.env \
  json-helper-mcp-server
```

## Development

### Building for Development

```bash
# Build with development dependencies
docker build --target development -t json-helper-mcp-server:dev .

# Run with code volume mount for live development
docker run -d \
  --name json-helper-mcp-server-dev \
  -p 8000:8000 \
  -p 8001:8001 \
  -v $(pwd)/src:/app/src \
  -e LOG_LEVEL=DEBUG \
  json-helper-mcp-server:dev
```

### Debugging

1. **Run with debug logging:**
   ```bash
   docker-compose up --build -e LOG_LEVEL=DEBUG
   ```

2. **Access container shell:**
   ```bash
   docker exec -it json-helper-mcp-server /bin/bash
   ```

3. **View real-time logs:**
   ```bash
   docker-compose logs -f json-helper-mcp-server
   ```

## Production Deployment

### Security Considerations

1. **Use specific image tags:**
   ```bash
   docker build -t json-helper-mcp-server:1.0.0 .
   ```

2. **Run as non-root user (already configured in Dockerfile)**

3. **Use secrets for sensitive data (if needed for future integrations):**
   ```yaml
   # docker-compose.yml
   services:
     json-helper-mcp-server:
       environment:
         - API_KEY_FILE=/run/secrets/api_key
       secrets:
         - api_key
   
   secrets:
     api_key:
       file: ./secrets/api_key.txt
   ```

### Resource Limits

```yaml
# docker-compose.yml
services:
  json-helper-mcp-server:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Scaling

```bash
# Scale to multiple instances
docker-compose up --scale json-helper-mcp-server=3
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Use different ports
   docker run -p 8080:8000 -p 8081:8001 json-helper-mcp-server
   ```

2. **Permission denied:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Container won't start:**
   ```bash
   # Check logs
   docker logs json-helper-mcp-server
   
   # Run interactively for debugging
   docker run -it --rm json-helper-mcp-server /bin/bash
   ```

4. **Health check failing:**
   ```bash
   # Check if health endpoint is accessible
   docker exec json-helper-mcp-server curl -f http://localhost:8001/health
   ```

### Performance Monitoring

```bash
# Monitor container stats
docker stats json-helper-mcp-server

# Monitor with docker-compose
docker-compose top
```

## Image Information

- **Base Image**: `python:3.12-slim`
- **Working Directory**: `/app`
- **User**: `app` (non-root)
- **Exposed Ports**: 8000, 8001
- **Health Check**: Enabled

## Cleanup

```bash
# Remove containers and images
docker-compose down --rmi all --volumes

# Remove all unused Docker resources
docker system prune -a
```

## Integration Examples

### With Nginx Reverse Proxy

```nginx
# nginx.conf
upstream mcp_server {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://mcp_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://localhost:8001/health;
    }
}
```

### With Docker Swarm

```yaml
# docker-stack.yml
version: '3.8'

services:
  json-helper-mcp-server:
    image: json-helper-mcp-server:latest
    ports:
      - "8000:8000"
      - "8001:8001"
    environment:
      - LOG_LEVEL=INFO
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

Deploy with:
```bash
docker stack deploy -c docker-stack.yml mcp-stack
