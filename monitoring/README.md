# PMOVES Monitoring Stack

A comprehensive monitoring solution for the PMOVES platform featuring Prometheus metrics, Langfuse LLM observability, Grafana dashboards, and centralized logging.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- At least 4GB RAM available for monitoring services
- Ports 3001, 3002, 6379, 9090, 9093, 3100, 8080, 9100, 9121 available

### 1. Start the Monitoring Stack

```bash
# Navigate to monitoring directory
cd monitoring

# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Or use the startup script (Linux/Mac)
./start-monitoring.sh
```

### 2. Access the Dashboards

- **Grafana**: http://localhost:3001 (admin/$GRAFANA_ADMIN_PASSWORD)
- **Prometheus**: http://localhost:9090
- **Langfuse**: http://localhost:3002
- **AlertManager**: http://localhost:9093

## 📊 Components

### Core Monitoring
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alert routing and notifications
- **Node Exporter**: System metrics
- **cAdvisor**: Container metrics

### LLM Observability
- **Langfuse**: LLM call tracing and analytics
- **PostgreSQL**: Langfuse database

### Logging
- **Loki**: Log aggregation
- **Promtail**: Log collection

### Infrastructure
- **Redis**: Caching and rate limiting

## 🔧 Configuration

### Environment Variables

Copy and customize the monitoring configuration:

```bash
cp monitoring.env.example monitoring.env
```

Key variables to configure:

```env
# Grafana
GRAFANA_ADMIN_PASSWORD=your-secure-password

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key

# Redis
REDIS_PASSWORD=your-redis-password

# Alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SMTP_FROM=alerts@yourdomain.com
```

### Service Integration

To integrate monitoring with your PMOVES services, add the monitoring module:

```python
from monitoring.pmoves_monitoring import init_monitoring

# Initialize monitoring
monitor = init_monitoring(
    service_name="pmoves-backend",
    langfuse_public_key="pk-lf-...",
    langfuse_secret_key="sk-lf-...",
    redis_url="redis://localhost:6379"
)

# Add metrics endpoint to FastAPI
@app.get("/metrics")
async def metrics():
    return Response(monitor.get_metrics(), media_type="text/plain")

# Use monitoring decorators
@monitor.monitor_function("process_request")
async def process_request():
    # Your code here
    pass

# Track LLM calls
with monitor.trace_llm_call("openai", "gpt-4") as trace:
    result = await llm_call()
    trace.update(tokens_used=150, cost=0.003)
```

## 📈 Dashboards

### PMOVES Platform Overview
The main dashboard includes:

- **Service Status**: Real-time health of all services
- **Request Metrics**: Rate, latency, and error rates
- **LLM Analytics**: Usage, costs, and performance
- **Agent Operations**: Agent-specific metrics
- **Search Performance**: Search latency and throughput
- **System Resources**: CPU, memory, and disk usage
- **Container Metrics**: Docker container performance

### Custom Dashboards
Create custom dashboards for specific use cases:

1. Go to Grafana → Create → Dashboard
2. Add panels with Prometheus queries
3. Use the PMOVES metrics (prefix: `pmoves_`)

## 🚨 Alerting

### Pre-configured Alerts

The monitoring stack includes alerts for:

- Service downtime
- High error rates
- Elevated response times
- Resource exhaustion
- LLM cost thresholds
- Rate limit violations

### Custom Alerts

Add custom alerts in `prometheus/rules/`:

```yaml
groups:
  - name: custom-alerts
    rules:
      - alert: CustomMetricHigh
        expr: custom_metric > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Custom metric is high"
```

### Notification Channels

Configure notifications in `alertmanager/alertmanager.yml`:

- Email notifications
- Slack integration
- Webhook endpoints
- PagerDuty integration

## 📋 Metrics Reference

### Core Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pmoves_requests_total` | Counter | Total HTTP requests |
| `pmoves_request_duration_seconds` | Histogram | Request duration |
| `pmoves_active_connections` | Gauge | Active connections |
| `pmoves_errors_total` | Counter | Total errors |

### LLM Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pmoves_llm_requests_total` | Counter | LLM API calls |
| `pmoves_llm_duration_seconds` | Histogram | LLM response time |
| `pmoves_llm_tokens_total` | Counter | Token usage |
| `pmoves_llm_cost_total` | Counter | LLM costs |

### Agent Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pmoves_agent_operations_total` | Counter | Agent operations |
| `pmoves_agent_response_seconds` | Histogram | Agent response time |

### Search Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pmoves_search_requests_total` | Counter | Search requests |
| `pmoves_search_duration_seconds` | Histogram | Search duration |

## 🔍 Logging

### Log Collection

Promtail collects logs from:
- Docker containers
- System logs
- Application logs

### Log Queries

Use LogQL in Grafana to query logs:

```logql
# All PMOVES backend logs
{container="pmoves-backend"}

# Error logs only
{container="pmoves-backend"} |= "ERROR"

# LLM-related logs
{container=~".*agent.*"} |= "llm"

# Rate limit violations
{container="pmoves-backend"} |= "rate_limit"
```

### Structured Logging

The monitoring module provides structured logging:

```python
monitor.log_info("Processing request", 
                 request_id="req-123", 
                 user_id="user-456",
                 operation="search")
```

## 🔧 Troubleshooting

### Common Issues

**Services not starting:**
```bash
# Check Docker resources
docker system df
docker system prune

# Check logs
docker-compose -f docker-compose.monitoring.yml logs [service]
```

**Grafana login issues:**
```bash
# Reset admin password
docker exec -it pmoves-grafana grafana-cli admin reset-admin-password newpassword
```

**Prometheus not scraping:**
- Check service discovery in Prometheus targets
- Verify network connectivity between containers
- Ensure metrics endpoints are accessible

**Langfuse connection issues:**
- Verify database connection
- Check environment variables
- Review Langfuse logs

### Performance Tuning

**High memory usage:**
- Adjust Prometheus retention: `--storage.tsdb.retention.time=15d`
- Reduce scrape intervals for non-critical metrics
- Configure Grafana query timeout

**Slow queries:**
- Add Prometheus recording rules for complex queries
- Use Grafana query caching
- Optimize dashboard refresh intervals

## 🔒 Security

### Access Control
- Change default passwords
- Enable HTTPS in production
- Configure firewall rules
- Use strong Redis passwords

### Data Protection
- Regular backups of Prometheus data
- Secure Langfuse database
- Log retention policies
- Sensitive data masking

## 📚 Advanced Usage

### Custom Metrics

Add custom metrics to your services:

```python
from prometheus_client import Counter, Histogram

# Custom counter
custom_operations = Counter('custom_operations_total', 
                           'Custom operations', 
                           ['operation_type'])

# Custom histogram
custom_duration = Histogram('custom_duration_seconds',
                           'Custom operation duration')

# Usage
custom_operations.labels(operation_type='data_processing').inc()
with custom_duration.time():
    # Your operation here
    pass
```

### Integration with CI/CD

Monitor deployments:

```yaml
# In your CI/CD pipeline
- name: Notify deployment
  run: |
    curl -X POST http://prometheus:9090/api/v1/admin/tsdb/delete_series \
         -d 'match[]=deployment_info{version="old"}'
```

### Scaling

For production scaling:

1. **Prometheus Federation**: Multiple Prometheus instances
2. **Grafana Clustering**: Load-balanced Grafana instances
3. **Loki Clustering**: Distributed Loki setup
4. **External Storage**: S3/GCS for long-term storage

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review service logs
3. Consult Grafana/Prometheus documentation
4. Open an issue in the PMOVES repository

## 🔄 Updates

To update the monitoring stack:

```bash
# Pull latest images
docker-compose -f docker-compose.monitoring.yml pull

# Restart services
docker-compose -f docker-compose.monitoring.yml up -d
```

---

**The PMOVES monitoring stack provides comprehensive observability for your AI platform, enabling proactive monitoring, performance optimization, and reliable operations.** 