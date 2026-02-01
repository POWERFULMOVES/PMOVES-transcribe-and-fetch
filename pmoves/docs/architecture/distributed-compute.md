# PMOVES.AI Distributed Compute Architecture

**Status:** Active Development
**Version:** 0.1.0
**Last Updated:** 2026-02-01

---

## Executive Summary

PMOVES.AI implements a **peer-to-peer compute marshaling network** that enables distributed AI workloads across heterogeneous hardware. The system automatically discovers nodes, classifies capabilities, and allocates work based on hardware tiers, GPU availability, and network topology.

### Key Design Principles

1. **Sovereign First** - Each node operates independently; no central coordinator required
2. **Capability-Based** - Work allocation based on measured hardware, not declarations
3. **Geometric Consensus** - CHIT (Compressed Hierarchical Information Transfer) for swarm coordination
4. **Observability Native** - All telemetry flows through TensorZero for visibility
5. **Graceful Degradation** - System continues operating with partial node failures

---

## Node Tier Classification

### Tiers

| Tier | Description | Hardware Requirements | Use Cases |
|------|-------------|----------------------|-----------|
| **AI_FACTORY** | High-end training | 24GB+ VRAM, 128GB+ RAM | Model training, fine-tuning |
| **WORKER_HUB** | Multi-GPU inference | 2+ GPUs, 64GB+ RAM | Batch inference, serving |
| **GPU_PEER** | Single GPU | 16GB+ VRAM, 32GB+ RAM | Distributed inference |
| **CPU_PEER** | CPU-only | 16GB+ RAM | Embeddings, preprocessing |
| **EDGE** | Low-power | ARM64 or <16GB RAM | Local inference, sensors |
| **DISASTER** | Air-gapped fallback | Minimum viable specs | Offline operation |

### Detection Logic

```python
# Pseudo-code for tier classification
def classify_node(gpu_vram_gb, gpu_count, ram_gb, is_arm=False):
    if is_arm or ram_gb < 16:
        return EDGE
    if gpu_count >= 1 and gpu_vram_gb >= 24 and ram_gb >= 128:
        return AI_FACTORY
    if gpu_count >= 2 and ram_gb >= 64:
        return WORKER_HUB
    if gpu_count >= 1 and gpu_vram_gb >= 16 and ram_gb >= 32:
        return GPU_PEER
    if ram_gb >= 16:
        return CPU_PEER
    return DISASTER
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PMOVES.AI P2P Network                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  AI_FACTORY  │    │  WORKER_HUB  │    │   GPU_PEER   │              │
│  │  (RTX 5090)  │    │  (2x RTX)    │    │  (1x GPU)    │              │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘              │
│         │                   │                   │                      │
│         └───────────────────┼───────────────────┘                      │
│                             │                                          │
│                    ┌────────▼────────┐                                │
│                    │   NATS JetStream │                                │
│                    │  (Event Bus)     │                                │
│                    └────────┬────────┘                                │
│                             │                                          │
│         ┌───────────────────┼───────────────────┐                     │
│         │                   │                   │                     │
│    ┌────▼─────┐      ┌─────▼────┐      ┌─────▼────┐                 │
│    │ Agent    │      │ Tensor   │      │ CHIT     │                 │
│    │ Zero     │      │ Zero     │      │ Geometry │                 │
│    │ (MCP)    │      │ (Gateway)│      │ Bus      │                 │
│    └────┬─────┘      └─────┬────┘      └─────┬────┘                 │
│         │                   │                   │                     │
│         └───────────────────┼───────────────────┘                     │
│                             │                                          │
│                    ┌────────▼────────┐                                │
│                    │  Work Allocator │                                │
│                    │  (Marshaling)   │                                │
│                    └─────────────────┘                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Deep Dive

### 1. Resource Detector Service

**Location:** `pmoves/services/resource-detector/`

**Purpose:** Detect system hardware and generate appropriate docker-compose resource limits.

**Classes:**

| Class | Purpose |
|-------|---------|
| `NodeTier` | Enum defining node capability tiers |
| `HardwareDetector` | Detects CPU, RAM, GPU via lscpu, free, pynvml |
| `HardwareProfile` | Complete hardware snapshot with tier classification |
| `ResourceAllocator` | Generates docker-compose resource limits |
| `NodeCapabilities` | P2P announcement message for node discovery |

**Example Usage:**

```python
from pmoves.services.resource_detector import get_hardware_profile

profile = get_hardware_profile()
print(f"Node tier: {profile.tier.value}")
print(f"CPU: {profile.cpu.total_threads} threads")
print(f"RAM: {profile.memory.total_gb:.1f}GB")
print(f"GPU: {len(profile.gpus)}x {profile.total_gpu_vram_gb:.1f}GB")
```

---

### 2. Node Registry (Planned: T2-1)

**NATS Subjects:**
- `compute.nodes.announce.v1` - Nodes publish capabilities on startup
- `compute.nodes.heartbeat.v1` - Liveness updates every 15s
- `compute.nodes.query.v1` - Query for available nodes

**Message Format:**

```json
{
  "node_id": "uuid-or-hostname",
  "hostname": "ai-factory-01",
  "tier": "ai_factory",
  "cpu_cores": 32,
  "cpu_threads": 64,
  "memory_gb": 192.0,
  "gpu_count": 1,
  "gpu_vram_gb": 32.0,
  "gpu_models": ["NVIDIA RTX 5090"],
  "ipv4": "192.168.1.100",
  "available_cpu_slots": 60,
  "available_gpu_slots": 1,
  "supported_models": ["llama-3", "mixtral"],
  "max_context_tokens": 32768
}
```

---

### 3. Work Allocator (Planned: T2-2)

**NATS Subjects:**
- `compute.work.offer.v1` - Node offers capacity
- `compute.work.request.v1` - Client requests compute
- `compute.work.claim.v1` - Work assigned to node
- `compute.work.result.v1` - Work completed

**Allocation Algorithm:**

1. **Filter by tier** - Only consider nodes meeting minimum tier requirement
2. **Check capacity** - Verify available CPU/GPU/RAM
3. **Score by utilization** - Prefer less utilized nodes
4. **Apply geometric constraints** - CHIT positioning for latency optimization
5. **Reserve resources** - Mark resources as in-use

---

### 4. CHIT Geometry Bus Integration

**Purpose:** Hyperbolic encoding of node positions for efficient swarm consensus.

**NATS Subjects:**
- `geometry.cgp.v1` - CGP (Compressed Geometry Packet) messages
- `tokenism.cgp.v1` - Economic transactions encoded geometrically

**Integration:**

Each node announces its position in hyperbolic space via `NodeCapabilities.geometric_position`. This enables:

- **Latency-aware routing** - Closer nodes in hyperbolic space = lower latency
- **Load balancing** - Geometric partitioning of work
- **Failure detection** - Missing heartbeat triggers geometric reconfiguration

---

### 5. TensorZero Observability

**Purpose:** Centralized LLM routing and telemetry.

**Integration Points:**

| Data Type | TensorZero Destination |
|-----------|------------------------|
| Resource usage | ClickHouse `resource_usage` table |
| Work requests | `/v1/chat/completions` with metadata |
| Node metrics | Custom metrics via Prometheus push |
| Training data | RL feedback loop (agent.rl.trajectory.v1) |

**ClickHouse Queries:**

```sql
-- Average resource utilization by tier
SELECT
    tier,
    avg(cpu_utilization) as avg_cpu,
    avg(memory_utilization) as avg_mem,
    avg(gpu_utilization) as avg_gpu
FROM resource_usage
WHERE timestamp > now() - INTERVAL 1 HOUR
GROUP BY tier;

-- Work completion by node
SELECT
    node_id,
    tier,
    count(*) as completed_jobs,
    avg(duration_seconds) as avg_duration
FROM work_requests
WHERE status = 'completed'
  AND timestamp > now() - INTERVAL 24 HOUR
GROUP BY node_id, tier
ORDER BY completed_jobs DESC;
```

---

## vLLM Integration (Planned: T3)

### Tensor Parallelism (TP)

Splits model weights across multiple GPUs on the same node.

**Configuration:**
```yaml
vllm:
  tensor_parallel_size: 2  # Number of GPUs per node
  max_model_len: 32768
  gpu_memory_utilization: 0.9
```

### Pipeline Parallelism (PP)

Distributes model layers across multiple nodes.

**Configuration:**
```yaml
vllm:
  pipeline_parallel_size: 4  # Number of nodes
  tensor_parallel_size: 2    # GPUs per node
```

### Auto-Sizing (T3-1-002)

The system automatically calculates optimal TP/PP sizes based on:

1. Available GPUs per node
2. Model size (parameters)
3. VRAM per GPU
4. Target context length

```python
def calculate_tp_size(model_params, vram_per_gpu, context_len):
    # Estimate memory per layer
    bytes_per_param = 2  # FP16
    layers = model_params_to_layers(model_params)
    layer_size = model_params * bytes_per_param / layers

    # Account for KV cache
    kv_cache = context_len * layers * 2 * 2  # 2 tokens, 2 bytes

    # Calculate TP size
    tp_size = 1
    while layer_size / tp_size + kv_cache > vram_per_gpu:
        tp_size *= 1

    return tp_size
```

---

## RL Feedback Loop (Planned: T7)

### Reward Components

| Component | Weight | Description |
|-----------|--------|-------------|
| `task_completion` | 0.40 | Binary reward for successful completion |
| `efficiency` | 0.20 | Inverse of resource usage (CPU/GPU time) |
| `code_quality` | 0.15 | Static analysis metrics |
| `user_feedback` | 0.25 | Explicit user ratings |

### NATS Subjects

- `agent.rl.trajectory.v1` - Agent action sequences with metadata
- `agent.rl.reward.v1` - Calculated rewards for trajectories
- `agent.rl.training.request.v1` - Trigger model retraining

### Data Flow

```
Agent Zero Action
    │
    ├──► TensorZero (request logged)
    │
    ├──► NATS agent.rl.trajectory.v1
    │       │
    │       └──► AgentGym-RL (replay buffer)
    │
    ├──► Task Completion
    │       │
    │       └──► Reward Calculation
    │               │
    │               └──► NATS agent.rl.reward.v1
    │                       │
    │                       └──► AgentGym-RL (training)
    │
    └──► Model Update
            │
            └──► Agent Zero (improved policy)
```

---

## llama-throughput-lab Integration (Planned: T4)

### Purpose

Benchmarking and validation of hardware capabilities before deployment.

### Workflow

1. **Pre-deployment** - Run llama-throughput-lab benchmark
2. **Validation** - Compare against expected performance for tier
3. **Publishing** - Results sent to TensorZero for tracking
4. **Optimization** - Automated parameter tuning based on results

### NATS Subjects

- `compute.benchmark.start.v1` - Trigger benchmark
- `compute.benchmark.result.v1` - Results published
- `compute.benchmark.optimization.v1` - Parameter recommendations

---

## Disaster Recovery

### Offline Mode

When network connectivity is lost, nodes can:

1. **Continue local inference** - Using cached models
2. **Queue work** - Store requests locally until reconnect
3. **Fallback to DISASTER tier** - Minimal resource mode

### Air-Gapped Deployment

1. **Pre-stage models** - Load all required models locally
2. **Disable NATS** - Use local work queue only
3. **Reduce monitoring** - Local logs only, no external telemetry

---

## Security Considerations

### Node Authentication

- **CGP Public Keys** - Each node has a unique CHIT geometric public key
- **JWT Tokens** - Work requests signed by requesting agent
- **IP Whitelisting** - Optional firewall rules for known subnets

### Resource Isolation

- **Docker resource limits** - Generated dynamically per service
- **cgroups enforcement** - Hardware-level resource guarantees
- **Network namespaces** - Separate networks per workload class

### Data Privacy

- **Local-only mode** - No data leaves the node
- **Encrypted transit** - TLS for all NATS communication
- **At-rest encryption** - MinIO buckets encrypted

---

## Monitoring and Observability

### Health Endpoints

All services expose:
- `/healthz` - Liveness check (returns 200 if healthy)
- `/metrics` - Prometheus metrics
- `/ready` - Readiness check (returns 503 if draining)

### Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `compute_nodes_total` | Gauge | Total nodes in network |
| `compute_nodes_online` | Gauge | Nodes with recent heartbeat |
| `compute_work_pending` | Gauge | Work awaiting assignment |
| `compute_work_active` | Gauge | Currently executing jobs |
| `compute_utilization_cpu` | Gauge | CPU utilization 0-1 |
| `compute_utilization_gpu` | Gauge | GPU utilization 0-1 |
| `compute_utilization_memory` | Gauge | Memory utilization 0-1 |

### Grafana Dashboards

1. **Network Overview** - Node status, tier distribution
2. **Work Allocation** - Request rate, completion time
3. **Resource Utilization** - CPU/GPU/RAM by tier
4. **CHIT Geometry** - Node positions in hyperbolic space

---

## Deployment Guide

### Prerequisites

1. **Hardware** - Minimum 16GB RAM, any GPU optional
2. **OS** - Linux (Ubuntu 22.04 recommended)
3. **Docker** - Version 24.0+
4. **NATS Server** - JetStream enabled

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/POWERFULMOVES/PMOVES.AI.git
cd PMOVES.AI

# 2. Configure environment
cp pmoves/.env.example pmoves/.env
# Edit pmoves/.env with your settings

# 3. Generate resource limits
python -m pmoves.services.resource_detector.generate \
    > pmoves/docker-compose.resource-override.yml

# 4. Start services
docker compose -f pmoves/docker-compose.hardened.yml \
    -f pmoves/docker-compose.resource-override.yml \
    --profile agents --profile workers up -d

# 5. Verify health
curl http://localhost:8080/healthz  # Agent Zero
curl http://localhost:3030/healthz  # TensorZero
```

### Node Registration

Nodes auto-register on startup by publishing to `compute.nodes.announce.v1`.

Manual registration:

```bash
nats pub 'compute.nodes.announce.v1' \
  '{"node_id":"my-node","tier":"gpu_peer",...}'
```

---

## Future Enhancements

| Track | Description | Status |
|-------|-------------|--------|
| T1 | Hardware detection foundation | 🟡 In Progress |
| T2 | P2P coordination (registry, marshaling) | ⚪ Planned |
| T3 | vLLM integration | ⚪ Planned |
| T4 | llama-throughput-lab benchmarks | ⚪ Planned |
| T5 | CHIT geometry bus | ⚪ Planned |
| T6 | TensorZero observability | ⚪ Planned |
| T7 | RL feedback loop | ⚪ Planned |
| T8 | Documentation & testing | ⚪ Planned |

---

## References

- **DISTRIBUTED_COMPUTE_ROADMAP.md** - Parallel execution roadmap
- **SUBSYSTEM_INTEGRATION.md** - BoTZ, DoX, Tokenism, Voice
- **CHIT_GEOMETRY_BUS.md** - Complete CHIT reference
- **PMOVES.AI Agentic Architecture Deep Dive.md** - Agent architecture
- **TensorZero Documentation** - https://docs.tensorzero.com
- **vLLM Documentation** - https://docs.vllm.ai

---

**Document Version:** 0.1.0
**Authors:** Opus 4.5 (PMOVES.AI Agent Team)
**License:** MIT
