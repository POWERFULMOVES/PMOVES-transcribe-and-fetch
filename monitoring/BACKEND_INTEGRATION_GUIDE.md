# PMOVES Backend Monitoring Integration Guide

## Overview

This guide provides step-by-step instructions to integrate the monitoring system with your existing 4,684-line PMOVES FastAPI backend and Supabase database.

## Quick Integration (5 minutes)

### Step 1: Add Monitoring to main.py

Add these lines to your `backend/app/main.py`:

```python
# Add at the top with other imports
from monitoring.backend_integration import setup_backend_monitoring

# After creating your FastAPI app instance
app = FastAPI(title="PMOVES Backend", version="1.0.0")

# Add this line to set up monitoring
monitor = setup_backend_monitoring(app, "pmoves-backend")

# Your existing code continues...
```

### Step 2: Environment Variables

Add to your `.env` file:

```env
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_HOST=http://localhost:3002

# Monitoring Configuration
REDIS_URL=redis://localhost:6379
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

### Step 3: Start Monitoring Stack

```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### Step 4: Verify Integration

Visit these URLs to confirm everything is working:
- **Backend Metrics**: http://localhost:8000/metrics
- **Backend Health**: http://localhost:8000/health
- **Monitoring Status**: http://localhost:8000/monitoring/status
- **Grafana Dashboard**: http://localhost:3001 (admin/$GRAFANA_ADMIN_PASSWORD)
- **Langfuse Traces**: http://localhost:3002

## Detailed Integration for Specific Components

### 1. Supabase Operations Monitoring

For your Supabase database operations, wrap your functions:

```python
from monitoring.backend_integration import monitor_supabase_operation

# Example: Wrap your existing Supabase functions
@monitor_supabase_operation("vector_search")
async def search_embeddings(query_vector, table_name):
    # Your existing Supabase search code
    result = await supabase.table(table_name).select("*").execute()
    return result

@monitor_supabase_operation("insert")
async def insert_content(table_name, data):
    # Your existing Supabase insert code
    result = await supabase.table(table_name).insert(data).execute()
    return result
```

### 2. Search Operations Monitoring (psearchworking.py)

For your 2,632-line search system:

```python
from monitoring.backend_integration import monitor_search_operation

# Wrap your search functions
@monitor_search_operation("vector")
async def vector_search(query, threshold=0.8):
    # Your existing vector search code from psearchworking.py
    results = await perform_vector_search(query, threshold)
    return results

@monitor_search_operation("hybrid")
async def hybrid_search(query, params):
    # Your existing hybrid search code
    results = await perform_hybrid_search(query, params)
    return results

@monitor_search_operation("keyword")
async def keyword_search(query):
    # Your existing keyword search code
    results = await perform_keyword_search(query)
    return results
```

### 3. Content Processing Monitoring (pmoves_upserter.py)

For your content management system:

```python
from monitoring.backend_integration import monitor_content_processing

# Wrap your content processing functions
@monitor_content_processing("video", "processing")
async def process_video(video_url):
    # Your existing video processing code
    result = await download_and_process_video(video_url)
    return result

@monitor_content_processing("markdown", "upsert")
async def upsert_markdown(content, metadata):
    # Your existing markdown upserting code
    result = await process_and_upsert_markdown(content, metadata)
    return result

@monitor_content_processing("web", "fetch")
async def fetch_web_content(url):
    # Your existing web content fetching code
    result = await fetch_and_process_url(url)
    return result
```

### 4. LLM Provider Monitoring

For your multi-provider LLM integration:

```python
from monitoring.backend_integration import monitor_llm_provider_call

# Wrap your LLM provider calls
@monitor_llm_provider_call("openai", "gpt-4")
async def call_openai_gpt4(messages, **kwargs):
    # Your existing OpenAI code
    response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        **kwargs
    )
    return response

@monitor_llm_provider_call("groq", "llama-3")
async def call_groq_llama(messages, **kwargs):
    # Your existing Groq code
    response = await groq_client.chat.completions.create(
        model="llama-3-70b",
        messages=messages,
        **kwargs
    )
    return response

@monitor_llm_provider_call("anthropic", "claude-3")
async def call_anthropic_claude(messages, **kwargs):
    # Your existing Anthropic code
    response = await anthropic_client.messages.create(
        model="claude-3-opus",
        messages=messages,
        **kwargs
    )
    return response
```

## Endpoint-Specific Integration

### Video Processing Endpoints

```python
from monitoring.backend_integration import BackendIntegrationHelpers

helpers = BackendIntegrationHelpers()

@app.post("/process-video/")
@helpers.wrap_video_processing()
async def process_video_endpoint(video_data: VideoRequest):
    # Your existing video processing endpoint code
    result = await process_video_logic(video_data)
    return result

@app.post("/api/download")
@helpers.wrap_content_fetch()
async def download_content_endpoint(download_request: DownloadRequest):
    # Your existing download endpoint code
    result = await download_logic(download_request)
    return result
```

### Search Endpoints

```python
@app.post("/api/vector-search")
@helpers.wrap_vector_search()
async def vector_search_endpoint(search_request: SearchRequest):
    # Your existing vector search endpoint code
    results = await vector_search_logic(search_request)
    return results

@app.post("/api/search")
@helpers.wrap_hybrid_search()
async def comprehensive_search_endpoint(search_request: SearchRequest):
    # Your existing comprehensive search endpoint code
    results = await comprehensive_search_logic(search_request)
    return results
```

### Content Management Endpoints

```python
@app.post("/fetch-content")
@helpers.wrap_content_fetch()
async def fetch_content_endpoint(fetch_request: FetchRequest):
    # Your existing content fetching endpoint code
    result = await fetch_content_logic(fetch_request)
    return result
```

## Agent Integration

### SupabaseAgent Integration

```python
# In your SupabaseAgent implementation
from monitoring.backend_integration import monitor_supabase_operation, monitor_search_operation

class SupabaseAgent:
    @monitor_search_operation("agent_search")
    async def search_content(self, query: str, search_type: str):
        # Your existing SupabaseAgent search code
        results = await self.perform_search(query, search_type)
        return results
    
    @monitor_supabase_operation("agent_upsert")
    async def upsert_content(self, content: dict):
        # Your existing SupabaseAgent upsert code
        result = await self.perform_upsert(content)
        return result
```

### TranscribeAgent Integration

```python
# In your TranscribeAgent implementation
from monitoring.backend_integration import monitor_content_processing, monitor_llm_provider_call

class TranscribeAgent:
    @monitor_content_processing("audio", "transcription")
    async def transcribe_audio(self, audio_file: str):
        # Your existing transcription code
        result = await self.perform_transcription(audio_file)
        return result
    
    @monitor_llm_provider_call("openai", "whisper")
    async def openai_transcribe(self, audio_data):
        # Your existing OpenAI Whisper code
        result = await openai.audio.transcriptions.create(...)
        return result
```

### MultimodalAgent Integration

```python
# In your MultimodalAgent implementation
from monitoring.backend_integration import monitor_content_processing, monitor_llm_provider_call

class MultimodalAgent:
    @monitor_content_processing("image", "analysis")
    async def analyze_image(self, image_data: bytes):
        # Your existing image analysis code
        result = await self.perform_image_analysis(image_data)
        return result
    
    @monitor_llm_provider_call("openai", "gpt-4-vision")
    async def vision_analysis(self, image_url: str, prompt: str):
        # Your existing vision analysis code
        result = await openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }]
        )
        return result
```

## Configuration for Your Environment

### Environment Variables

Create `monitoring/.env` with your specific configuration:

```env
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-your-actual-key
LANGFUSE_SECRET_KEY=sk-lf-your-actual-secret
LANGFUSE_HOST=http://localhost:3002

# Supabase Configuration (for monitoring integration)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key

# OpenAI Configuration (for examples)
OPENAI_API_KEY=your-openai-key

# Groq Configuration
GROQ_API_KEY=your-groq-key

# Anthropic Configuration
ANTHROPIC_API_KEY=your-anthropic-key

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Monitoring Configuration
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=your-secure-password
```

### Docker Compose Override

Create `monitoring/docker-compose.override.yml` for your specific needs:

```yaml
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
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - ./custom-dashboards:/etc/grafana/provisioning/dashboards/custom
  
  prometheus:
    ports:
      - "${PROMETHEUS_PORT}:9090"
    volumes:
      - ./prometheus/custom-rules:/etc/prometheus/rules/custom
```

## Testing the Integration

### 1. Basic Health Check

```bash
# Test backend health with monitoring
curl http://localhost:8000/health

# Expected response:
{
  "service": "pmoves-backend",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "redis": "healthy",
    "langfuse": "healthy"
  }
}
```

### 2. Metrics Verification

```bash
# Check Prometheus metrics
curl http://localhost:9090/api/v1/targets

# Verify metrics endpoint
curl http://localhost:8000/metrics
```

### 3. Langfuse Trace Verification

```bash
# Check monitoring status
curl http://localhost:8000/monitoring/status

# Expected response:
{
  "service": "pmoves-backend",
  "monitoring_enabled": true,
  "langfuse_enabled": true,
  "prometheus_enabled": true,
  "structured_logging": true,
  "current_trace_url": "http://localhost:3002/trace/..."
}
```

### 4. Test a Monitored Endpoint

```python
# Test script to verify monitoring
import requests
import time

# Make a request to a monitored endpoint
response = requests.post("http://localhost:8000/api/vector-search", json={
    "query": "test search",
    "threshold": 0.8
})

print(f"Response: {response.status_code}")

# Check Grafana dashboard at http://localhost:3001
# Check Langfuse traces at http://localhost:3002
```

## Troubleshooting

### Common Issues

1. **Langfuse Connection Failed**
   ```bash
   # Check Langfuse service
   docker-compose -f docker-compose.monitoring.yml logs langfuse-server
   
   # Verify environment variables
   echo $LANGFUSE_PUBLIC_KEY
   ```

2. **Metrics Not Appearing**
   ```bash
   # Check Prometheus targets
   curl http://localhost:9090/api/v1/targets
   
   # Verify metrics endpoint
   curl http://localhost:8000/metrics
   ```

3. **Redis Connection Issues**
   ```bash
   # Check Redis service
   docker-compose -f docker-compose.monitoring.yml logs redis
   
   # Test Redis connection
   redis-cli ping
   ```

### Debug Mode

Enable debug mode for detailed logging:

```python
import os
os.environ["LANGFUSE_DEBUG"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"

# Restart your backend service
```

## Performance Considerations

### Monitoring Overhead

The monitoring system is designed to have minimal performance impact:

- **Request Middleware**: ~1-2ms overhead per request
- **Langfuse Tracing**: Async, non-blocking
- **Prometheus Metrics**: In-memory counters, minimal overhead
- **Structured Logging**: Async logging to prevent blocking

### Production Optimizations

```python
# For production, consider these optimizations
monitor = setup_backend_monitoring(
    app, 
    "pmoves-backend",
    # Reduce sampling for high-traffic endpoints
    langfuse_sample_rate=0.1,  # Sample 10% of traces
    # Disable debug logging
    log_level="INFO"
)
```

## Next Steps

1. **Deploy Monitoring Stack**: Start the Docker Compose monitoring services
2. **Integrate Backend**: Add monitoring to your main.py and key functions
3. **Test Integration**: Verify metrics and traces are working
4. **Configure Dashboards**: Customize Grafana dashboards for your needs
5. **Set Up Alerts**: Configure AlertManager for your production environment

## Support

- **Integration Issues**: Check the troubleshooting section above
- **Custom Metrics**: Refer to `pmoves_monitoring.py` for additional metrics
- **Dashboard Customization**: See Grafana documentation for custom panels
- **Langfuse Features**: Visit https://langfuse.com/docs for advanced features 