# PMOVES Supabase Agent

A FastAPI-based agent that provides comprehensive Supabase database interaction capabilities for the PMOVES platform.

## Features

- **Database Operations**: Query, insert, update, and delete operations
- **Table Management**: Create, modify, and manage Supabase tables
- **Real-time Chat Integration**: Listen for chat messages and respond with database operations
- **Agent Framework Integration**: Auto-registration with the PMOVES platform
- **LiteLLM Integration**: AI-powered responses and processing
- **Streaming Results**: Efficiently handle large datasets with streaming responses
- **CLI Interface**: Command-line tools for testing and management

## Quick Start

### 1. Configuration

Copy the environment template:
```bash
# Windows
copy env-template.txt .env

# Linux/Mac
cp env-template.txt .env
```

Edit `.env` with your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### 2. Build and Run (Windows)

```powershell
# Build the Docker image
.\build.ps1

# Run standalone
.\run.ps1 -Mode standalone

# Run with full PMOVES platform
.\run.ps1 -Mode platform

# Run in detached mode
.\run.ps1 -Mode standalone -Detached
```

### 3. Build and Run (Linux/Mac)

```bash
# Build the Docker image
docker build -t pmoves-supabase-agent .

# Run standalone
docker-compose up

# Run with full platform
docker-compose -f ../docker-compose.yml up
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | Required |
| `SUPABASE_KEY` | Your Supabase API key | Required |
| `AGENT_PORT` | Port for the FastAPI service | 8002 |
| `AGENT_REGISTRY_URL` | URL for agent registration | http://localhost:8000/agents |
| `LITELLM_PROXY_URL` | LiteLLM proxy URL for AI features | http://litellm-proxy:4000 |
| `LOG_LEVEL` | Logging level | INFO |

### Agent Framework Settings

The agent supports advanced configuration through JSON environment variables:

```env
AGENT_CAPABILITIES=["supabase_interaction", "query_execution", "data_upsert", "table_management"]
AGENT_TAGS=["database", "supabase", "data"]
AGENT_CONFIG={"max_query_limit": 1000, "allow_ddl": false}
```

## API Endpoints

### Health Check
```
GET /health
```

### Database Operations

#### Upsert Data
```
POST /upsert-data
{
  "table_name": "my_table",
  "data": {"column1": "value1", "column2": "value2"},
  "conflict_on": "id"
}
```

#### Stream Results
```
POST /stream-results
{
  "table_name": "my_table",
  "chunk_size": 50,
  "query_params": {
    "select": "id,name,created_at",
    "filters": [["status", "eq", "active"]],
    "order_by": "created_at.desc"
  }
}
```

#### Infinite Query (Pagination)
```
POST /infinite-query
{
  "table_name": "my_table",
  "page": 1,
  "page_size": 20,
  "filter_params": [
    {"field": "status", "operator": "eq", "value": "active"}
  ],
  "order_params": {"field": "created_at", "ascending": false}
}
```

#### Table Management
```
POST /manage-table
{
  "operation": "create_table",
  "table_name": "new_table",
  "schema": {
    "columns": [
      {"name": "id", "type": "SERIAL PRIMARY KEY"},
      {"name": "data", "type": "TEXT"}
    ]
  }
}
```

## CLI Usage

The agent includes a comprehensive CLI for testing and management:

### Basic Commands

```bash
# Check agent health
python cli.py status

# Adjust agent parameters
python cli.py adjust-params '{"allow_table_management_ddl": true}'

# Upsert data
python cli.py upsert-data my_table '{"id": 1, "name": "Test"}' --conflict-on id

# Stream results
python cli.py stream-results my_table --filters '[["status","eq","active"]]'

# Send chat message (for testing chat integration)
python cli.py send-chat-message user123 session456 "Hello, agent!"
```

### Advanced Operations

```bash
# Create a table
python cli.py manage-table create_table new_stuff --schema '{"columns": [{"name": "id", "type": "INTEGER PRIMARY KEY"}, {"name": "value", "type": "TEXT"}]}'

# Add a column
python cli.py manage-table add_column new_stuff --column-def '{"name": "extra_info", "type": "BOOLEAN DEFAULT FALSE"}'

# Paginated query
python cli.py infinite-query my_table --filters '[{"field": "status", "operator": "eq", "value": "active"}]' --page 1 --page-size 10
```

## Architecture

### Components

1. **FastAPI Application** (`app/main.py`): Main API server
2. **Agent Framework** (`app/utils/agent_framework.py`): Platform integration
3. **Chat Listener** (`app/chat_listener.py`): Real-time chat integration
4. **LLM Registry Service** (`app/utils/llm_registry_service.py`): AI capabilities
5. **CLI Interface** (`cli.py`): Command-line tools

### Integration Points

- **Backend Registration**: Auto-registers with the PMOVES backend
- **LiteLLM Proxy**: Routes AI requests through the platform proxy
- **Chat System**: Listens for messages and responds with database operations
- **Health Monitoring**: Provides health checks and metrics

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp env-template.txt .env
# Edit .env with your configuration
```

3. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker Development

Mount the app directory for live reloading:
```yaml
volumes:
  - ./app:/app/app
```

### Testing

```bash
# Run health check
curl http://localhost:8002/health

# Test API endpoints
curl -X POST http://localhost:8002/upsert-data \
  -H "Content-Type: application/json" \
  -d '{"table_name": "test", "data": {"id": 1, "name": "test"}}'
```

## Platform Integration

### With PMOVES Backend

The agent automatically registers with the PMOVES backend and provides:
- Health status reporting
- Capability advertisement
- Service discovery
- Centralized logging

### With LiteLLM Proxy

AI-powered features are routed through the platform's LiteLLM proxy:
- Natural language query processing
- Intelligent data analysis
- Automated response generation

### With Other Agents

The agent can communicate with other platform agents:
- Pipecat agents for real-time conversations
- Crawl4AI agents for data enrichment
- Custom agents for specialized tasks

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   ```
   Error: Failed to connect to agent at http://localhost:8002/health
   ```
   - Check if the agent is running: `docker ps`
   - Verify port mapping: `docker port pmoves-supabase-agent`
   - Check logs: `docker logs pmoves-supabase-agent`

2. **Supabase Authentication Error**:
   ```
   Error: SUPABASE_URL and SUPABASE_KEY must be set
   ```
   - Verify `.env` file exists and contains correct credentials
   - Check Supabase project settings for correct URL and key

3. **Agent Registration Failed**:
   ```
   Warning: Agent registration failed
   ```
   - Ensure backend is running and accessible
   - Check `AGENT_REGISTRY_URL` configuration
   - Verify network connectivity between containers

### Logs and Debugging

```bash
# View agent logs
docker logs pmoves-supabase-agent -f

# Check container status
docker ps | grep supabase-agent

# Test network connectivity
docker exec pmoves-supabase-agent curl http://litellm-proxy:4000/health
```

## Security Considerations

- **API Keys**: Store Supabase keys securely, never commit to version control
- **DDL Operations**: Table management operations are disabled by default
- **Network Access**: Agent communicates only within the Docker network
- **Input Validation**: All API inputs are validated using Pydantic models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the PMOVES platform. See the main project license for details. 