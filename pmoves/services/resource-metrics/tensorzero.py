"""TensorZero integration for resource metrics.

Publishes resource usage metrics to TensorZero for tracking
and analysis in the central observability system.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    import logging
    httpx = None
    logging.warning("httpx not installed, TensorZero publishing disabled")

from .collector import ResourceMetrics

logger = logging.getLogger(__name__)


class TensorZeroMetricsPublisher:
    """Publish resource metrics to TensorZero."""

    def __init__(
        self,
        tensorzero_url: str = "http://localhost:3030",
        batch_size: int = 10,
        batch_timeout_seconds: float = 30.0,
    ):
        """Initialize TensorZero metrics publisher.

        Args:
            tensorzero_url: TensorZero gateway URL
            batch_size: Number of metrics to batch before sending
            batch_timeout_seconds: Max time to wait before sending batch
        """
        self.tensorzero_url = tensorzero_url
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout_seconds

        self._metric_queue: List[Dict] = []
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start background flush task."""
        if self._running:
            return

        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())
        logger.info("TensorZero metrics publisher started")

    async def stop(self):
        """Stop publisher and flush remaining metrics."""
        if not self._running:
            return

        self._running = False

        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Flush remaining metrics
        if self._metric_queue:
            await self._flush()

        logger.info("TensorZero metrics publisher stopped")

    async def publish(self, metrics: ResourceMetrics, labels: Optional[Dict] = None):
        """Publish metrics to TensorZero.

        Args:
            metrics: ResourceMetrics to publish
            labels: Optional labels to attach to metrics
        """
        if httpx is None:
            logger.debug("Skipping publish: httpx not available")
            return

        payload = {
            "timestamp": metrics.timestamp.isoformat(),
            "metrics": metrics.to_dict(),
            "labels": labels or {},
        }

        self._metric_queue.append(payload)

        # Flush if batch is full
        if len(self._metric_queue) >= self.batch_size:
            await self._flush()

    async def publish_batch(self, metrics_list: List[ResourceMetrics], labels: Optional[Dict] = None):
        """Publish multiple metrics at once.

        Args:
            metrics_list: List of ResourceMetrics to publish
            labels: Optional labels to attach to all metrics
        """
        for metrics in metrics_list:
            await self.publish(metrics, labels)

    async def _flush_loop(self):
        """Background loop for periodic flushing."""
        while self._running:
            try:
                await asyncio.sleep(self.batch_timeout)

                if self._metric_queue:
                    await self._flush()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in flush loop: {e}")

    async def _flush(self):
        """Flush queued metrics to TensorZero."""
        if not self._metric_queue:
            return

        batch = self._metric_queue.copy()
        self._metric_queue.clear()

        url = f"{self.tensorzero_url}/metrics/resource"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json={"metrics": batch},
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    logger.debug(f"Flushed {len(batch)} metrics to TensorZero")
                else:
                    logger.warning(
                        f"Failed to flush metrics to TensorZero: "
                        f"{response.status_code} - {response.text}"
                    )
                    # Re-queue on failure
                    self._metric_queue.extend(batch)

        except Exception as e:
            logger.error(f"Error flushing metrics to TensorZero: {e}")
            # Re-queue on failure
            self._metric_queue.extend(batch)

    async def query_metrics(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """Query metrics from TensorZero.

        Args:
            start_time: Start of query range
            end_time: End of query range
            filters: Optional filters to apply

        Returns:
            List of metric records
        """
        url = f"{self.tensorzero_url}/metrics/resource/query"

        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
        if filters:
            params["filters"] = filters

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=params,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("metrics", [])
                else:
                    logger.warning(f"Query failed: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Error querying metrics: {e}")
            return []


class TensorZeroInferenceMetrics:
    """Track inference-specific metrics for TensorZero."""

    def __init__(
        self,
        tensorzero_url: str = "http://localhost:3030",
        service_name: str = "pmoves-orchestrator",
    ):
        """Initialize inference metrics tracker.

        Args:
            tensorzero_url: TensorZero gateway URL
            service_name: Name of this service
        """
        self.tensorzero_url = tensorzero_url
        self.service_name = service_name

    async def track_inference(
        self,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        gpu_utilization: float,
        memory_mb: int,
        metadata: Optional[Dict] = None,
    ):
        """Track an inference request.

        Args:
            model_name: Name of the model
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            latency_ms: Request latency in milliseconds
            gpu_utilization: GPU utilization during inference (0-100)
            memory_mb: GPU memory used in MB
            metadata: Optional metadata to attach
        """
        if httpx is None:
            logger.debug("Skipping inference tracking: httpx not available")
            return

        url = f"{self.tensorzero_url}/v1/inference_metrics"

        payload = {
            "service": self.service_name,
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "latency_ms": latency_ms,
                "tokens_per_second": (completion_tokens * 1000 / latency_ms) if latency_ms > 0 else 0,
            },
            "resources": {
                "gpu_utilization_percent": gpu_utilization,
                "gpu_memory_mb": memory_mb,
            },
            "metadata": metadata or {},
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code != 200:
                    logger.debug(f"Failed to track inference: {response.status_code}")

        except Exception as e:
            logger.debug(f"Error tracking inference: {e}")

    async def track_model_load(
        self,
        model_name: str,
        load_time_ms: float,
        vram_mb: int,
        gpu_count: int,
        success: bool,
        error: Optional[str] = None,
    ):
        """Track a model load operation.

        Args:
            model_name: Name of the model
            load_time_ms: Time to load model in milliseconds
            vram_mb: VRAM used by model
            gpu_count: Number of GPUs used
            success: Whether load was successful
            error: Error message if failed
        """
        if httpx is None:
            logger.debug("Skipping model load tracking: httpx not available")
            return

        url = f"{self.tensorzero_url}/metrics/model_load"

        payload = {
            "service": self.service_name,
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "load_time_ms": load_time_ms,
            "vram_mb": vram_mb,
            "gpu_count": gpu_count,
            "success": success,
            "error": error,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
        except Exception as e:
            logger.debug(f"Error tracking model load: {e}")

    async def get_model_stats(
        self,
        model_name: Optional[str] = None,
        time_window_hours: float = 24.0,
    ) -> Dict:
        """Get aggregated statistics for a model.

        Args:
            model_name: Model name (None for all models)
            time_window_hours: Time window in hours

        Returns:
            Dict with aggregated stats
        """
        if httpx is None:
            return {"error": "httpx not available"}

        url = f"{self.tensorzero_url}/metrics/model_stats"

        params = {
            "time_window_hours": time_window_hours,
        }
        if model_name:
            params["model"] = model_name

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    return response.json()
                else:
                    return {}

        except Exception as e:
            logger.error(f"Error getting model stats: {e}")
            return {}


async def run_publisher(
    tensorzero_url: str = "http://localhost:3030",
    collector=None,
):
    """Run metrics publisher as standalone service.

    Args:
        tensorzero_url: TensorZero gateway URL
        collector: Optional ResourceCollector instance
    """
    from .collector import ResourceCollector

    publisher = TensorZeroMetricsPublisher(tensorzero_url)
    await publisher.start()

    if collector is None:
        collector = ResourceCollector()
        await collector.start()

    try:
        while True:
            await asyncio.sleep(5)

            # Collect and publish metrics
            metrics = await collector.collect()
            await publisher.publish(metrics, {"source": "resource-metrics"})

    except asyncio.CancelledError:
        pass
    finally:
        await publisher.stop()
        await collector.stop()


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    tensorzero_url = os.getenv("TENSORZERO_URL", "http://localhost:3030")

    try:
        asyncio.run(run_publisher(tensorzero_url))
    except KeyboardInterrupt:
        logger.info("Publisher stopped by user")
