#!/bin/bash

# PMOVES Monitoring Stack Startup Script
# This script starts the complete monitoring infrastructure

set -e

echo "🚀 Starting PMOVES Monitoring Stack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating monitoring directories..."
mkdir -p prometheus/data
mkdir -p grafana/data
mkdir -p loki/data
mkdir -p alertmanager/data

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R 472:472 grafana/data  # Grafana user
sudo chown -R 65534:65534 prometheus/data  # Nobody user
sudo chown -R 10001:10001 loki/data  # Loki user

# Load environment variables
if [ -f monitoring.env ]; then
    echo "📋 Loading environment variables..."
    export $(cat monitoring.env | grep -v '^#' | xargs)
else
    echo "⚠️  monitoring.env not found. Using default values."
fi

# Start the monitoring stack
echo "🐳 Starting monitoring containers..."
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

services=(
    "prometheus:9090"
    "grafana:3001"
    "langfuse-server:3002"
    "redis:6379"
    "loki:3100"
    "alertmanager:9093"
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -f -s "http://localhost:$port" > /dev/null 2>&1; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is not responding"
    fi
done

echo ""
echo "🎉 PMOVES Monitoring Stack is ready!"
echo ""
echo "📊 Access URLs:"
echo "   Grafana:     http://localhost:3001 (admin/\$GRAFANA_ADMIN_PASSWORD)"
echo "   Prometheus:  http://localhost:9090"
echo "   Langfuse:    http://localhost:3002"
echo "   AlertManager: http://localhost:9093"
echo "   Loki:        http://localhost:3100"
echo ""
echo "📈 Default Grafana Dashboard: PMOVES Platform Overview"
echo "🔍 Logs: Check Loki datasource in Grafana"
echo "🚨 Alerts: Configure AlertManager for notifications"
echo ""
echo "To stop the monitoring stack:"
echo "   docker-compose -f docker-compose.monitoring.yml down"
echo ""
echo "To view logs:"
echo "   docker-compose -f docker-compose.monitoring.yml logs -f [service-name]" 