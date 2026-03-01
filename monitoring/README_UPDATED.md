# PMOVES Monitoring Stack - Updated with Langfuse Python SDK

## Overview

The PMOVES monitoring stack provides comprehensive observability for the AI platform with updated Langfuse Python SDK integration. This implementation uses the latest `@observe()` decorator pattern for seamless LLM tracing and observability.

## 🆕 What's New in This Update

### Langfuse Python SDK v2.6.3+ Integration
- **Modern `@observe()` decorator** for automatic function tracing
- **Native OpenAI integration** with `langfuse.openai` wrapper
- **Simplified context management** with `langfuse_context`
- **Automatic trace correlation** with structured logging
- **Enhanced scoring and evaluation** capabilities

### Key Improvements
- Simplified LLM tracing with decorators
- Better error handling and context propagation
- Automatic token usage and cost tracking
- Enhanced debugging and development experience

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PMOVES App    │    │   Monitoring    │    │   Langfuse      │
│                 │    │   Stack         │    │   Platform      │
│ @observe()      │───▶│                 │───▶│                 │
│ decorators      │    │ • Prometheus    │    │ • Traces        │
│                 │    │ • Grafana       │    │ • Generations   │
│ langfuse.openai │    │ • Loki          │    │ • Evaluations   │
│ integration     │    │ • AlertManager  │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp monitoring.env.example monitoring.env

# Edit with your configuration
nano monitoring.env
```

Required environment variables:
```env
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_HOST=http://localhost:3002  # or https://cloud.langfuse.com

# OpenAI Configuration (for examples)
OPENAI_API_KEY=sk-your-openai-key

# Monitoring Configuration
GRAFANA_ADMIN_PASSWORD=CHANGE_ME
REDIS_URL=redis://localhost:6379
```

### 2. Start Monitoring Stack

```bash
# Start all monitoring services
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Check service status
docker-compose -f docker-compose.monitoring.yml ps
```

### 3. Access Dashboards

- **Grafana**: http://localhost:3001 (admin/$GRAFANA_ADMIN_PASSWORD)
- **Prometheus**: http://localhost:9090
- **Langfuse**: http://localhost:3002
- **AlertManager**: http://localhost:9093

### 4. Basic Usage

```python
from monitoring.pmoves_monitoring import init_monitoring
from langfuse.decorators import observe
from langfuse.openai import openai

# Initialize monitoring
monitor = init_monitoring(service_name="my-service")

# Simple LLM call with automatic tracing
@observe()
def my_llm_function(prompt: str):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Call the function - automatically traced!
result = my_llm_function("Hello, world!")
```

## Core Features

### 1. Automatic LLM Tracing

```python
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import openai

@observe()
def analyze_content(content: str):
    # Update trace metadata
    langfuse_context.update_current_trace(
        name="Content Analysis",
        user_id="user-123",
        tags=["analysis", "content"]
    )
    
    # LLM call - automatically traced
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Analyze the content"},
            {"role": "user", "content": content}
        ]
    )
    
    # Score the operation
    langfuse_context.score_current_observation(
        name="analysis_quality",
        value=0.9,
        comment="High quality analysis"
    )
    
    return response.choices[0].message.content
```

### 2. Agent Operation Monitoring

```python
from monitoring.pmoves_monitoring import observe_agent_operation

@observe_agent_operation("supabase", "search")
def search_database(query: str):
    # Automatic metrics tracking for agent operations
    results = supabase_client.search(query)
    return results
```

### 3. Custom LLM Provider Integration

```python
from monitoring.pmoves_monitoring import observe_llm_call

@observe_llm_call(name="Anthropic Claude Call")
def call_anthropic(prompt: str):
    # Custom LLM provider with automatic metrics
    response = anthropic_client.messages.create(
        model="claude-3-opus",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Update with usage details
    langfuse_context.update_current_observation(
        model="anthropic/claude-3-opus",
        usage_details={
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    )
    
    return response.content[0].text
```

### 4. Multi-Step Pipelines

```python
@observe()
def multi_step_pipeline(user_query: str):
    # Step 1: Understanding
    understanding = understand_query(user_query)
    
    # Step 2: Generation
    content = generate_content(understanding)
    
    # Step 3: Refinement
    refined = refine_content(content)
    
    # Score the entire pipeline
    langfuse_context.score_current_trace(
        name="pipeline_success",
        value=1.0,
        comment="Pipeline completed successfully"
    )
    
    return refined

@observe(name="Query Understanding")
def understand_query(query: str):
    # Nested observation - automatically linked
    return openai.chat.completions.create(...)

@observe(name="Content Generation")
def generate_content(understanding: dict):
    # Another nested observation
    return openai.chat.completions.create(...)
```

### 5. Error Handling and Monitoring

```python
@observe()
def robust_operation(data: str):
    try:
        result = process_data(data)
        
        # Score success
        langfuse_context.score_current_observation(
            name="operation_success",
            value=1.0
        )
        
        return result
        
    except Exception as e:
        # Log error with context
        monitor.log_error("Operation failed", 
                         error=str(e), 
                         data_length=len(data))
        
        # Score failure
        langfuse_context.score_current_observation(
            name="operation_success",
            value=0.0,
            comment=f"Failed: {str(e)}"
        )
        
        # Track error metrics
        monitor.track_error("processing_error", "error")
        
        raise
```

### 6. Async Operations

```python
@observe()
async def async_batch_processing(items: List[str]):
    langfuse_context.update_current_trace(
        name="Batch Processing",
        metadata={"batch_size": len(items)}
    )
    
    results = []
    for item in items:
        # Each operation automatically traced
        result = await process_item(item)
        results.append(result)
    
    return results

@observe()
async def process_item(item: str):
    # Async LLM call - automatically traced
    response = await openai.chat.completions.acreate(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": item}]
    )
    return response.choices[0].message.content
```

## Monitoring Components

### Prometheus Metrics

The system automatically tracks:

- **Request Metrics**: `pmoves_requests_total`, `pmoves_request_duration_seconds`
- **LLM Metrics**: `pmoves_llm_requests_total`, `pmoves_llm_tokens_total`, `pmoves_llm_cost_total`
- **Agent Metrics**: `pmoves_agent_operations_total`, `pmoves_agent_response_seconds`
- **Error Metrics**: `pmoves_errors_total`, `pmoves_rate_limit_hits_total`

### Structured Logging

All logs include:
- Correlation IDs
- Langfuse trace IDs
- Service context
- Operation metadata

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "message": "LLM call completed",
  "service": "pmoves-backend",
  "trace_id": "pmoves-backend-abc123",
  "langfuse_trace_id": "lf-trace-xyz789",
  "operation": "content_analysis",
  "duration": 2.1,
  "tokens_used": 150
}
```

### Langfuse Tracing

Automatic capture of:
- Function execution traces
- LLM call generations
- Token usage and costs
- Custom metadata and scores
- Error tracking and debugging

## Advanced Configuration

### Custom Monitoring Setup

```python
from monitoring.pmoves_monitoring import PMOVESMonitoring

# Custom monitoring instance
monitor = PMOVESMonitoring(
    service_name="custom-service",
    langfuse_public_key="pk-lf-...",
    langfuse_secret_key="sk-lf-...",
    langfuse_host="https://cloud.langfuse.com",
    redis_url="redis://localhost:6379",
    enable_prometheus=True,
    enable_langfuse=True,
    enable_structured_logging=True
)

# Custom function monitoring
@monitor.monitor_function("custom_operation")
def my_function():
    # Automatic metrics + Langfuse tracing
    pass
```

### Environment Configuration

```env
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-your-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_DEBUG=false
LANGFUSE_SAMPLE_RATE=1.0

# Monitoring Configuration
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
REDIS_URL=redis://localhost:6379

# Service Configuration
SERVICE_NAME=pmoves-backend
LOG_LEVEL=INFO
```

### Docker Compose Override

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  langfuse-server:
    environment:
      - LANGFUSE_CSP_ENFORCE_HTTPS=false
      - LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES=true
    ports:
      - "3002:3000"
  
  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your-secure-password
    volumes:
      - ./custom-dashboards:/etc/grafana/provisioning/dashboards/custom
```

## Troubleshooting

### Common Issues

1. **Langfuse Connection Failed**
   ```bash
   # Check Langfuse service
   docker-compose logs langfuse-server
   
   # Verify environment variables
   echo $LANGFUSE_PUBLIC_KEY
   ```

2. **Missing Traces**
   ```python
   # Ensure flush is called
   from langfuse.decorators import langfuse_context
   
   # At end of application
   langfuse_context.flush()
   ```

3. **OpenAI Integration Issues**
   ```python
   # Use Langfuse OpenAI wrapper
   from langfuse.openai import openai  # Not from openai directly
   ```

### Debug Mode

```python
import os
os.environ["LANGFUSE_DEBUG"] = "true"

# Or in monitoring initialization
monitor = init_monitoring(
    service_name="debug-service",
    # ... other params
)
```

### Health Checks

```python
# Check monitoring health
health = await monitor.health_check()
print(health)

# Check Langfuse connection
from langfuse.decorators import langfuse_context
langfuse_context.auth_check()
```

## Examples

See `monitoring/examples/langfuse_integration_example.py` for comprehensive examples including:

1. Simple LLM calls with automatic tracing
2. Complex agent operations with custom metadata
3. Multi-step pipelines with nested observations
4. Error handling with scoring
5. Async operations with batch processing
6. Custom LLM provider integration

## Migration from Previous Version

### Key Changes

1. **Replace context managers with decorators**:
   ```python
   # Old
   with monitor.trace_llm_call("openai", "gpt-4") as trace:
       result = llm_call()
       trace.update(tokens_used=150)
   
   # New
   @observe()
   def llm_call():
       return openai.chat.completions.create(...)  # Auto-traced
   ```

2. **Use Langfuse OpenAI integration**:
   ```python
   # Old
   import openai
   
   # New
   from langfuse.openai import openai
   ```

3. **Update context management**:
   ```python
   # Old
   monitor.set_trace_context(trace_id)
   
   # New
   langfuse_context.update_current_trace(user_id="123")
   ```

## Production Deployment

### Security Considerations

1. **Secure API Keys**: Use environment variables or secrets management
2. **Network Security**: Isolate monitoring network
3. **Access Control**: Configure Grafana authentication
4. **Data Retention**: Set appropriate retention policies

### Scaling

1. **Prometheus**: Configure federation for multi-instance setups
2. **Langfuse**: Use cloud instance for production scale
3. **Redis**: Configure clustering for high availability
4. **Grafana**: Set up high availability configuration

### Monitoring the Monitoring

1. **Service Health**: Monitor monitoring service uptime
2. **Data Flow**: Ensure metrics and traces are flowing
3. **Storage**: Monitor disk usage and retention
4. **Performance**: Track monitoring overhead

## Support

- **Documentation**: See `OBSERVABILITY_IMPLEMENTATION_REVIEW.md`
- **Examples**: Check `examples/` directory
- **Issues**: Create GitHub issues for bugs
- **Langfuse Docs**: https://langfuse.com/docs/sdk/python/decorators

## License

This monitoring implementation is part of the PMOVES platform and follows the same licensing terms. 