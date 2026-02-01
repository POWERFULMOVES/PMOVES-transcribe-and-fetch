# Distributed Compute: Standalone Integration Guide

Guide for PMOVES submodules to integrate with distributed compute services when running standalone (undocked from main PMOVES.AI docker-compose).

## Overview

When a PMOVES submodule runs outside the main docker-compose (standalone mode), it can still:

1. **Register as a compute node** - Announce GPU/CPU resources to the mesh
2. **Receive distributed work** - Process inference tasks via NATS
3. **Query available resources** - Find other nodes for collaborative work
4. **Deploy vLLM instances** - Dynamically deploy LLMs with optimal configuration

## Prerequisites

### PMOVES.AI Services Running

The parent PMOVES.AI stack must be running with compute services enabled:

```bash
# On the PMOVES.AI host
cd /home/pmoves/PMOVES.AI
docker compose --profile compute up -d
```

Required services:
- `node-registry` (port 8082)
- `vllm-orchestrator` (port 8099)
- `gpu-orchestrator` (port 8098)
- `work-marshaling` (port 8100)
- `nats` (port 4222)

### Network Connectivity

The standalone node must be able to reach the PMOVES.AI host:

- Same physical machine: Use `localhost` or `127.0.0.1`
- Same local network: Use host's LAN IP (e.g., `192.168.1.100`)
- Docker-to-Host: Use `host.docker.internal` (see Docker configuration below)

## Docker Configuration

### For Linux

Add `host.docker.internal` to your `docker-compose.yml`:

```yaml
services:
  your-submodule:
    # ... other config ...
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### For macOS / Windows

`host.docker.internal` is available by default.

### Network Example

```yaml
version: '3.8'

services:
  my-submodule:
    build: .
    container_name: my-submodule
    environment:
      # Compute service URLs (via host gateway)
      NODE_REGISTRY_URL: http://host.docker.internal:8082
      VLLM_ORCHESTRATOR_URL: http://host.docker.internal:8099
      WORK_MARSHALING_URL: http://host.docker.internal:8100
      NATS_URL: nats://host.docker.internal:4222
      GPU_ORCHESTRATOR_URL: http://host.docker.internal:8098
    extra_hosts:
      - "host.docker.internal:host-gateway"
    # ... rest of config ...
```

## Integration Patterns

### 1. Register as a Compute Node

Your submodule can register itself as a compute node, making its resources available to the mesh.

```python
import asyncio
import httpx
import os
from datetime import datetime

async def register_as_compute_node():
    """Register with PMOVES.AI node registry."""

    # Detect your local resources
    capabilities = await detect_local_hardware()

    registry_url = os.environ.get("NODE_REGISTRY_URL", "http://host.docker.internal:8082")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{registry_url}/api/v1/nodes/register",
            json={
                "node_id": os.environ.get("NODE_ID", "my-submodule-node"),
                "hostname": os.environ.get("HOSTNAME", "submodule-host"),
                "tier": capabilities["tier"],
                "ipv4": get_local_ip(),
                "cpu": capabilities["cpu"],
                "memory": capabilities["memory"],
                "gpus": capabilities.get("gpus", []),
                "timestamp": datetime.now().isoformat(),
            },
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

async def detect_local_hardware():
    """Detect local CPU, GPU, and RAM."""
    # Your hardware detection logic
    return {
        "tier": "GPU_PEER",
        "cpu": {"cores": 16, "threads": 32, "model_name": "Ryzen 9"},
        "memory": {"total_gb": 64, "available_gb": 60},
        "gpus": [
            {"index": 0, "name": "RTX 4090", "vram_gb": 24}
        ]
    }
```

### 2. Connect to Work Marshaling

Subscribe to work assignments from the mesh:

```python
import nats
import json
import os

async def connect_to_work_marshal():
    """Connect to PMOVES.AI work marshaling."""

    nats_url = os.environ.get("NATS_URL", "nats://host.docker.internal:4222")

    nc = await nats.connect(nats_url)

    async def on_work_assigned(msg):
        """Handle incoming work assignment."""
        work = json.loads(msg.data)

        print(f"Received work: {work['work_id']}")

        try:
            # Process the work
            result = await process_inference(work)

            # Publish completion
            await nc.publish(
                "compute.work.completed.v1",
                json.dumps({
                    "work_id": work["work_id"],
                    "node_id": os.environ.get("NODE_ID"),
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                }).encode()
            )
        except Exception as e:
            # Publish failure
            await nc.publish(
                "compute.work.failed.v1",
                json.dumps({
                    "work_id": work["work_id"],
                    "node_id": os.environ.get("NODE_ID"),
                    "error": str(e),
                    "failed_at": datetime.now().isoformat()
                }).encode()
            )

    # Subscribe to work assignments
    await nc.subscribe("compute.work.assigned.v1", cb=on_work_assigned)

    # Keep connection alive
    while True:
        await asyncio.sleep(1)

async def process_inference(work):
    """Process inference work."""
    # Your inference logic here
    return {
        "output": "generated text...",
        "tokens_per_second": 45.2
    }
```

### 3. Request vLLM Deployment

Ask the orchestrator to deploy a vLLM instance with optimal configuration:

```python
import asyncio
import httpx
import os

async def deploy_vllm_instance(model_name: str):
    """Request vLLM deployment via orchestrator."""

    orchestrator_url = os.environ.get(
        "VLLM_ORCHESTRATOR_URL",
        "http://host.docker.internal:8099"
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{orchestrator_url}/api/v1/vllm/deploy",
            json={
                "model_name": model_name,
                "instance_name": f"{model_name.replace('/', '-')}-main",
                "auto_start": True
            },
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()

        print(f"vLLM deployed at: {result['endpoints']['api']}")
        return result
```

### 4. Query Available Nodes

Find other compute nodes in the mesh:

```python
import asyncio
import httpx
import os

async def find_gpu_nodes(min_vram_gb: int = 16):
    """Query for available GPU nodes."""

    registry_url = os.environ.get(
        "NODE_REGISTRY_URL",
        "http://host.docker.internal:8082"
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{registry_url}/api/v1/nodes/query",
            json={
                "requires_gpu": True,
                "min_tier": "gpu_peer",
                "online_only": True,
                "min_vram_gb": min_vram_gb
            },
            timeout=10.0
        )
        response.raise_for_status()
        result = response.json()

        print(f"Found {len(result['nodes'])} available nodes")
        return result["nodes"]
```

## Environment Variables

Add to your submodule's `.env` or `docker-compose.yml`:

```bash
# Distributed Compute Integration
NODE_REGISTRY_URL=http://host.docker.internal:8082
VLLM_ORCHESTRATOR_URL=http://host.docker.internal:8099
GPU_ORCHESTRATOR_URL=http://host.docker.internal:8098
WORK_MARSHALING_URL=http://host.docker.internal:8100
NATS_URL=nats://host.docker.internal:4222

# Node Identity (optional, defaults generated)
NODE_ID=my-submodule-node
HOSTNAME=submodule-host

# For direct LAN connection (alternative to host.docker.internal)
# NODE_REGISTRY_URL=http://192.168.1.100:8082
# NATS_URL=nats://192.168.1.100:4222
```

## Complete Example: Worker Node

Here's a complete example of a submodule that registers as a worker node:

```python
"""PMOVES.AI Compute Worker - Standalone Integration Example."""

import asyncio
import logging
import os
import signal
from datetime import datetime

import httpx
import nats

logger = logging.getLogger(__name__)

class ComputeWorker:
    """Worker node that processes distributed compute work."""

    def __init__(self):
        self.node_id = os.environ.get("NODE_ID", "worker-node")
        self.registry_url = os.environ.get(
            "NODE_REGISTRY_URL",
            "http://host.docker.internal:8082"
        )
        self.nats_url = os.environ.get(
            "NATS_URL",
            "nats://host.docker.internal:4222"
        )
        self._nc = None
        self._running = False

    async def start(self):
        """Start the worker."""
        logger.info(f"Starting worker: {self.node_id}")

        # Register with node registry
        await self._register_node()

        # Connect to NATS
        await self._connect_nats()

        self._running = True

        # Start heartbeat loop
        asyncio.create_task(self._heartbeat_loop())

        logger.info("Worker started successfully")

    async def stop(self):
        """Stop the worker."""
        self._running = False
        if self._nc:
            await self._nc.close()
        logger.info("Worker stopped")

    async def _register_node(self):
        """Register with the node registry."""
        capabilities = await self._detect_capabilities()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.registry_url}/api/v1/nodes/register",
                json={
                    "node_id": self.node_id,
                    "hostname": os.environ.get("HOSTNAME", "worker"),
                    "tier": capabilities["tier"],
                    "cpu": capabilities["cpu"],
                    "memory": capabilities["memory"],
                    "gpus": capabilities.get("gpus", []),
                },
                timeout=10.0
            )
            response.raise_for_status()
            logger.info("Registered with node registry")

    async def _connect_nats(self):
        """Connect to NATS and subscribe to work."""
        self._nc = await nats.connect(self.nats_url)

        # Subscribe to work assignments
        await self._nc.subscribe(
            "compute.work.assigned.v1",
            cb=self._on_work_assigned
        )

        logger.info("Connected to NATS")

    async def _on_work_assigned(self, msg):
        """Handle work assignment."""
        work = self._nc.payload(msg) if hasattr(self._nc, 'payload') else msg.data
        import json
        work = json.loads(work)

        logger.info(f"Received work: {work['work_id']}")

        try:
            result = await self._process_work(work)

            # Publish completion
            await self._nc.publish(
                "compute.work.completed.v1",
                json.dumps({
                    "work_id": work["work_id"],
                    "node_id": self.node_id,
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                }).encode()
            )
            logger.info(f"Work completed: {work['work_id']}")

        except Exception as e:
            # Publish failure
            await self._nc.publish(
                "compute.work.failed.v1",
                json.dumps({
                    "work_id": work["work_id"],
                    "node_id": self.node_id,
                    "error": str(e),
                    "failed_at": datetime.now().isoformat()
                }).encode()
            )
            logger.error(f"Work failed: {work['work_id']}: {e}")

    async def _process_work(self, work):
        """Process work item."""
        # Implement your work processing logic here
        await asyncio.sleep(1)  # Simulate work
        return {"output": "work completed"}

    async def _detect_capabilities(self):
        """Detect local hardware capabilities."""
        # Implement hardware detection
        return {
            "tier": "CPU_ONLY",
            "cpu": {"cores": 4, "threads": 8},
            "memory": {"total_gb": 16, "available_gb": 12}
        }

    async def _heartbeat_loop(self):
        """Send periodic heartbeats."""
        while self._running:
            try:
                # Heartbeat logic would go here
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break

async def main():
    """Main entry point."""
    worker = ComputeWorker()

    # Handle shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(worker.stop()))

    await worker.start()

    # Keep running
    while worker._running:
        await asyncio.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())
```

## Testing Your Integration

### 1. Verify Connectivity

```bash
# Test node registry
curl http://host.docker.internal:8082/healthz

# Test NATS
docker run --rm --network host nats \
  nats sub "compute.nodes.announce.v1"

# Test work marshaling
curl http://host.docker.internal:8100/healthz
```

### 2. Test Work Flow

```bash
# Submit test work
curl -X POST http://host.docker.internal:8100/api/v1/work/submit \
  -H "Content-Type: application/json" \
  -d '{
    "work_type": "test",
    "priority": 1,
    "payload": {"test": true}
  }'
```

### 3. Monitor NATS Traffic

```bash
# Watch all compute subjects
nats sub "compute.>"
```

## Troubleshooting

### Cannot connect to host.docker.internal

**Linux:** Add `extra_hosts` to docker-compose.yml:
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**Alternative:** Use LAN IP directly:
```bash
NODE_REGISTRY_URL=http://192.168.1.100:8082
```

### NATS connection refused

Verify PMOVES.AI services are running:
```bash
curl http://localhost:4222/varz  # NATS monitoring
```

Check if ports are exposed in PMOVES.AI docker-compose:
```yaml
ports:
  - "4222:4222"  # NATS
  - "8082:8082"  # Node Registry
```

### Work not being received

1. Check if node is registered:
   ```bash
   curl http://host.docker.internal:8082/api/v1/nodes
   ```

2. Verify NATS subscription:
   ```bash
   nats sub "compute.work.assigned.v1"
   ```

3. Check work marshaling logs:
   ```bash
   docker logs work-marshaling
   ```

## Security Considerations

### Production Deployment

For production use:

1. **Enable NATS TLS:**
   ```bash
   NATS_URL=tls://nats.example.com:4222
   ```

2. **Use authentication:**
   ```bash
   NATS_USER=username
   NATS_PASSWORD=password
   ```

3. **Restrict node registration:**
   - Add API key to registration endpoint
   - Validate node certificates

4. **Network isolation:**
   - Use VPN for inter-node communication
   - Firewall rules to restrict access

## See Also

- [Distributed Compute Services](./DISTRIBUTED_COMPUTE_SERVICES.md)
- [NATS Subjects Catalog](../../.claude/context/nats-subjects.md)
- [PMOVES.AI Developer Context](../../.claude/CLAUDE.md)
