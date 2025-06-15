# PMOVES Pipecat Agents

Production-ready AI agents for the PMOVES platform with comprehensive multimodal capabilities, advanced security features, and seamless integration.

## 🚀 Features

### Core Agent Types

#### 1. SupabaseAgent
- **Database Operations**: Full CRUD operations with Supabase
- **Vector Search**: Semantic search with embeddings
- **Content Upserting**: Intelligent content management
- **Real-time Sync**: Live database synchronization
- **Security**: SQL injection protection, input validation

#### 2. TranscribeAgent  
- **Multi-Provider Support**: OpenAI Whisper, Groq, Deepgram
- **Format Support**: MP3, WAV, MP4, WebM, and more
- **Language Detection**: Automatic language identification
- **Batch Processing**: Efficient bulk transcription
- **Quality Control**: Confidence scoring and validation

#### 3. MultimodalAgent
- **Vision Analysis**: Image understanding with GPT-4V, Claude, Gemini
- **Image Generation**: DALL-E, Stable Diffusion integration
- **Audio Processing**: Transcription, emotion analysis, classification
- **Screen Capture**: Cross-platform screenshot capabilities
- **File Security**: Comprehensive upload validation

### 🔒 Production Security Features

#### Rate Limiting
- Redis-backed sliding window rate limiting
- Per-endpoint and per-user limits
- Burst protection and graceful degradation
- Configurable limits and windows

#### Authentication & Authorization
- API key authentication
- JWT token support
- Role-based access control
- Secure session management

#### Input Validation & Sanitization
- SQL injection protection
- XSS prevention
- Path traversal detection
- File upload security
- JSON depth validation

#### Security Headers
- HSTS, CSP, X-Frame-Options
- CORS configuration
- Content type validation
- Security event logging

## 📦 Installation

### Prerequisites
- Python 3.9+
- Redis (for rate limiting)
- Docker (recommended)

### Quick Start

1. **Clone and Install**
```bash
git clone <repository>
cd pmoves-pipecat-agent
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run Agent**
```bash
# Supabase Agent
AGENT_TYPE=supabase python agent.py

# Transcribe Agent  
AGENT_TYPE=transcribe python agent.py

# Multimodal Agent
AGENT_TYPE=multimodal python agent.py

# Query provider capabilities
curl "http://pipecat:8080/provider_capabilities?model=gpt-3.5-turbo&provider=openai"

# Example Multimodal Pipeline
# (see `multimodal_pipeline.py` for a runnable stub)
```

## ⚙️ Configuration

### Environment Variables

#### Core Configuration
```bash
# Agent Configuration
AGENT_TYPE=supabase|transcribe|multimodal
AGENT_NAME=MyAgent
PORT=8000

# Pipecat Service
PIPECAT_SERVICE_URL=http://pipecat:8080
PIPECAT_WS_URL=ws://pipecat:8081

# Chat Configuration
CHAT_CHANNEL=main-room
CALL_WORD=@MyAgent
HEARTBEAT_INTERVAL=30
ENABLE_TRACING=false
# Optional conversation identifier for tracing
CONVERSATION_ID=
```

#### Security Configuration
```bash
# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
REDIS_URL=redis://localhost:6379

# Authentication
AUTH_ENABLED=true
API_KEYS=key1,key2,key3
JWT_SECRET=your-secret-key

# Request Limits
MAX_REQUEST_SIZE=10485760
MAX_FILE_SIZE=52428800
```

#### Provider API Keys
```bash
# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
DEEPGRAM_API_KEY=...
GOOGLE_API_KEY=...

# Database
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...

# Services
BACKEND_URL=http://pmoves-backend:8000
LITELLM_PROXY_URL=http://litellm-proxy:4000
```

## 🎯 Usage Examples

### Chat Commands

#### SupabaseAgent
```
@SupabaseAgent search machine learning
@SupabaseAgent query users select name
@SupabaseAgent upsert New content here
@SupabaseAgent health
```

#### TranscribeAgent
```
@TranscribeAgent transcribe https://example.com/audio.mp3
@TranscribeAgent providers
@TranscribeAgent health
```

#### MultimodalAgent
```
@MultimodalAgent analyze https://example.com/image.jpg What's in this image?
@MultimodalAgent generate A beautiful sunset over mountains
@MultimodalAgent screenshot
@MultimodalAgent providers
```

### API Usage

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Configuration
```bash
curl http://localhost:8000/config
```

#### With Authentication
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
curl -H "Authorization: Bearer your-jwt-token" http://localhost:8000/health
```

## 🏗️ Architecture

### Agent Structure
```
pmoves-pipecat-agent/
├── agent.py                 # Main agent client
├── agents/                  # Specialized agent implementations
│   ├── __init__.py
│   ├── supabase_agent.py   # Database operations
│   ├── transcribe_agent.py # Audio transcription
│   └── multimodal_agent.py # Multimodal AI
├── security/               # Security middleware
│   ├── __init__.py
│   └── middleware.py       # Comprehensive security
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

### Security Layers
1. **Network Security**: HTTPS, security headers
2. **Authentication**: API keys, JWT tokens
3. **Rate Limiting**: Redis-backed sliding window
4. **Input Validation**: SQL injection, XSS, path traversal
5. **File Security**: Magic number validation, quarantine
6. **Logging**: Security event monitoring

## 🔧 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

### Docker Development
```bash
docker build -t pmoves-agent .
docker run -p 8000:8000 --env-file .env pmoves-agent
```

## 📊 Monitoring

### Health Endpoints
- `/health` - Basic health status
- `/config` - Agent configuration
- `/metrics` - Performance metrics (if enabled)

### Logging
- Security events logged to stdout/file
- Request/response logging configurable
- Structured logging with JSON format

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🚀 Production Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  supabase-agent:
    build: .
    environment:
      - AGENT_TYPE=supabase
      - AGENT_NAME=SupabaseAgent
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - pipecat

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pmoves-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pmoves-agent
  template:
    metadata:
      labels:
        app: pmoves-agent
    spec:
      containers:
      - name: agent
        image: pmoves-agent:latest
        env:
        - name: AGENT_TYPE
          value: "supabase"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## 🔐 Security Best Practices

### Production Checklist
- [ ] Enable authentication (`AUTH_ENABLED=true`)
- [ ] Configure strong API keys
- [ ] Set up Redis for rate limiting
- [ ] Configure appropriate CORS origins
- [ ] Enable security headers
- [ ] Set up monitoring and alerting
- [ ] Regular security audits
- [ ] Keep dependencies updated

### Security Configuration
```bash
# Recommended production settings
AUTH_ENABLED=true
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=3600
SECURITY_HEADERS_ENABLED=true
SECURITY_LOGGING_ENABLED=true
MAX_REQUEST_SIZE=5242880
MAX_FILE_SIZE=26214400
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run security checks
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [Full docs](https://docs.pmoves.com)
- **Issues**: [GitHub Issues](https://github.com/pmoves/issues)
- **Discord**: [Community Chat](https://discord.gg/pmoves)
- **Email**: support@pmoves.com

## 🎉 Acknowledgments

- Pipecat AI for the core framework
- Supabase for real-time infrastructure
- OpenAI, Anthropic, and other AI providers
- The open-source community 