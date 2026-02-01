"""Resource Metrics Service - System monitoring for TensorZero integration.

Collects CPU, GPU, RAM, disk, and network metrics and publishes
them to TensorZero for centralized observability.

Usage:
    from pmoves.services.resource_metrics import (
        ResourceCollector,
        ResourceMetrics,
        TensorZeroMetricsPublisher,
        run_collector,
    )

    # Collect metrics
    collector = ResourceCollector()
    metrics = await collector.collect()
    print(f"CPU: {metrics.cpu_percent}%")
    print(f"Memory: {metrics.memory_percent}%")

    # Run as standalone service
    await run_collector()

NATS Integration:
    The service can be run alongside other orchestrator services
    to provide comprehensive resource visibility for the PMOVES
    distributed compute network.
"""

from .collector import (
    ResourceCollector,
    ResourceMetrics,
    run_collector,
)

from .tensorzero import (
    TensorZeroInferenceMetrics,
    TensorZeroMetricsPublisher,
    run_publisher,
)

__all__ = [
    # Collector
    "ResourceCollector",
    "ResourceMetrics",
    "run_collector",
    # TensorZero
    "TensorZeroMetricsPublisher",
    "TensorZeroInferenceMetrics",
    "run_publisher",
]
