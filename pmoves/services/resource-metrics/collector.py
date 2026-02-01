"""Resource metrics collector for TensorZero integration.

Collects CPU, GPU, RAM, and network metrics for observability.
Publishes to Prometheus and TensorZero for tracking.
"""

import asyncio
import logging
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class ResourceMetrics:
    """Snapshot of resource usage at a point in time."""

    timestamp: datetime

    # CPU metrics
    cpu_percent: float
    cpu_count: int
    cpu_freq_mhz: float

    # Memory metrics
    memory_total_mb: int
    memory_used_mb: int
    memory_available_mb: int
    memory_percent: float

    # GPU metrics (if available)
    gpu_count: int = 0
    gpu_utilization_percent: float = 0.0
    gpu_memory_used_mb: int = 0
    gpu_memory_total_mb: int = 0
    gpu_temperature_c: float = 0.0
    gpu_power_draw_w: float = 0.0

    # Disk metrics
    disk_total_gb: float = 0.0
    disk_used_gb: float = 0.0
    disk_percent: float = 0.0

    # Network metrics
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu": {
                "percent": round(self.cpu_percent, 2),
                "count": self.cpu_count,
                "freq_mhz": round(self.cpu_freq_mhz, 2),
            },
            "memory": {
                "total_mb": self.memory_total_mb,
                "used_mb": self.memory_used_mb,
                "available_mb": self.memory_available_mb,
                "percent": round(self.memory_percent, 2),
            },
            "gpu": {
                "count": self.gpu_count,
                "utilization_percent": round(self.gpu_utilization_percent, 2),
                "memory_used_mb": self.gpu_memory_used_mb,
                "memory_total_mb": self.gpu_memory_total_mb,
                "temperature_c": round(self.gpu_temperature_c, 2),
                "power_draw_w": round(self.gpu_power_draw_w, 2),
            } if self.gpu_count > 0 else None,
            "disk": {
                "total_gb": round(self.disk_total_gb, 2),
                "used_gb": round(self.disk_used_gb, 2),
                "percent": round(self.disk_percent, 2),
            },
            "network": {
                "sent_mb": round(self.network_sent_mb, 2),
                "recv_mb": round(self.network_recv_mb, 2),
            },
        }

    def to_prometheus(self) -> str:
        """Convert to Prometheus metric format."""
        lines = [
            f"# HELP pmoves_cpu_percent CPU utilization percentage",
            f"# TYPE pmoves_cpu_percent gauge",
            f"pmoves_cpu_percent {self.cpu_percent}",
            "",
            f"# HELP pmoves_memory_percent Memory utilization percentage",
            f"# TYPE pmoves_memory_percent gauge",
            f"pmoves_memory_percent {self.memory_percent}",
            "",
            f"# HELP pmoves_memory_used_mb Memory used in MB",
            f"# TYPE pmoves_memory_used_mb gauge",
            f"pmoves_memory_used_mb {self.memory_used_mb}",
        ]

        if self.gpu_count > 0:
            lines.extend([
                "",
                f"# HELP pmoves_gpu_utilization GPU utilization percentage",
                f"# TYPE pmoves_gpu_utilization gauge",
                f"pmoves_gpu_utilization {self.gpu_utilization_percent}",
                "",
                f"# HELP pmoves_gpu_memory_used_mb GPU memory used in MB",
                f"# TYPE pmoves_gpu_memory_used_mb gauge",
                f"pmoves_gpu_memory_used_mb {self.gpu_memory_used_mb}",
                "",
                f"# HELP pmoves_gpu_temperature_c GPU temperature in Celsius",
                f"# TYPE pmoves_gpu_temperature_c gauge",
                f"pmoves_gpu_temperature_c {self.gpu_temperature_c}",
                "",
                f"# HELP pmoves_gpu_power_draw_w GPU power draw in Watts",
                f"# TYPE pmoves_gpu_power_draw_w gauge",
                f"pmoves_gpu_power_draw_w {self.gpu_power_draw_w}",
            ])

        return "\n".join(lines)


# Import dataclass after ResourceMetrics is defined
from dataclasses import dataclass


class ResourceCollector:
    """Collect system resource metrics."""

    def __init__(
        self,
        poll_interval_seconds: float = 5.0,
        history_size: int = 60,
        track_gpu: bool = True,
    ):
        """Initialize resource collector.

        Args:
            poll_interval_seconds: How often to collect metrics
            history_size: Number of historical snapshots to keep
            track_gpu: Whether to track GPU metrics
        """
        self.poll_interval = poll_interval_seconds
        self.history_size = history_size
        self.track_gpu = track_gpu

        self._history: List[ResourceMetrics] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None

        # Track network I/O deltas
        self._last_network_io: Optional[Dict] = None

    async def collect(self) -> ResourceMetrics:
        """Collect current resource metrics.

        Returns:
            ResourceMetrics with current values
        """
        timestamp = datetime.now()

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else 0.0

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_total_mb = memory.total // (1024 * 1024)
        memory_used_mb = memory.used // (1024 * 1024)
        memory_available_mb = memory.available // (1024 * 1024)
        memory_percent = memory.percent

        # GPU metrics (if available)
        gpu_metrics = await self._collect_gpu_metrics()

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024**3)
        disk_used_gb = disk.used / (1024**3)
        disk_percent = disk.percent

        # Network metrics
        network_sent_mb = 0.0
        network_recv_mb = 0.0
        net_io = psutil.net_io_counters()
        if net_io:
            if self._last_network_io:
                # Calculate delta
                sent_delta = net_io.bytes_sent - self._last_network_io["bytes_sent"]
                recv_delta = net_io.bytes_recv - self._last_network_io["bytes_recv"]
                network_sent_mb = sent_delta / (1024 * 1024)
                network_recv_mb = recv_delta / (1024 * 1024)
            self._last_network_io = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
            }

        return ResourceMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            cpu_freq_mhz=cpu_freq_mhz,
            memory_total_mb=memory_total_mb,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            memory_percent=memory_percent,
            **gpu_metrics,
            disk_total_gb=disk_total_gb,
            disk_used_gb=disk_used_gb,
            disk_percent=disk_percent,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
        )

    async def _collect_gpu_metrics(self) -> Dict:
        """Collect GPU metrics using nvidia-smi.

        Returns:
            Dict with GPU metrics
        """
        if not self.track_gpu:
            return {
                "gpu_count": 0,
                "gpu_utilization_percent": 0.0,
                "gpu_memory_used_mb": 0,
                "gpu_memory_total_mb": 0,
                "gpu_temperature_c": 0.0,
                "gpu_power_draw_w": 0.0,
            }

        try:
            # Query GPU utilization, memory, temperature, and power
            result = await asyncio.to_thread(
                subprocess.run,
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return self._empty_gpu_metrics()

            # Aggregate across all GPUs
            gpu_count = 0
            total_utilization = 0.0
            total_memory_used = 0
            total_memory_total = 0
            total_temperature = 0.0
            total_power = 0.0

            for line in result.stdout.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 5:
                    gpu_count += 1
                    try:
                        total_utilization += float(parts[0])
                        total_memory_used += int(parts[1])
                        total_memory_total += int(parts[2])
                        total_temperature += float(parts[3])
                        total_power += float(parts[4])
                    except ValueError:
                        continue

            if gpu_count == 0:
                return self._empty_gpu_metrics()

            return {
                "gpu_count": gpu_count,
                "gpu_utilization_percent": total_utilization / gpu_count,
                "gpu_memory_used_mb": total_memory_used,
                "gpu_memory_total_mb": total_memory_total,
                "gpu_temperature_c": total_temperature / gpu_count,
                "gpu_power_draw_w": total_power / gpu_count,
            }

        except Exception as e:
            logger.debug(f"Could not collect GPU metrics: {e}")
            return self._empty_gpu_metrics()

    @staticmethod
    def _empty_gpu_metrics() -> Dict:
        """Return empty GPU metrics when GPU is unavailable."""
        return {
            "gpu_count": 0,
            "gpu_utilization_percent": 0.0,
            "gpu_memory_used_mb": 0,
            "gpu_memory_total_mb": 0,
            "gpu_temperature_c": 0.0,
            "gpu_power_draw_w": 0.0,
        }

    async def start(self):
        """Start background metric collection."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Resource collector started")

    async def stop(self):
        """Stop background collection."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Resource collector stopped")

    async def _poll_loop(self):
        """Background polling loop."""
        while self._running:
            try:
                metrics = await self.collect()
                self._history.append(metrics)

                # Keep history bounded
                if len(self._history) > self.history_size:
                    self._history.pop(0)

                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
                await asyncio.sleep(self.poll_interval)

    def get_history(self) -> List[ResourceMetrics]:
        """Get metric history.

        Returns:
            List of historical metrics
        """
        return self._history.copy()

    def get_average(self, window_seconds: float = 60.0) -> Optional[Dict]:
        """Calculate average metrics over a time window.

        Args:
            window_seconds: Time window to average

        Returns:
            Dict with averaged metrics
        """
        if not self._history:
            return None

        now = datetime.now()
        window_metrics = [
            m for m in self._history
            if (now - m.timestamp).total_seconds() <= window_seconds
        ]

        if not window_metrics:
            return None

        count = len(window_metrics)
        return {
            "cpu_percent": sum(m.cpu_percent for m in window_metrics) / count,
            "memory_percent": sum(m.memory_percent for m in window_metrics) / count,
            "gpu_utilization_percent": sum(m.gpu_utilization_percent for m in window_metrics) / count,
            "sample_count": count,
            "window_seconds": window_seconds,
        }

    def get_stats(self) -> Dict:
        """Get collector statistics.

        Returns:
            Dict with collector stats
        """
        return {
            "status": "running" if self._running else "stopped",
            "history_size": len(self._history),
            "poll_interval_seconds": self.poll_interval,
            "track_gpu": self.track_gpu,
        }


async def run_collector(
    poll_interval_seconds: float = 5.0,
    history_size: int = 60,
):
    """Run resource collector as standalone service.

    Args:
        poll_interval_seconds: Polling interval
        history_size: History buffer size
    """
    collector = ResourceCollector(poll_interval_seconds, history_size)

    await collector.start()

    try:
        # Keep running
        while True:
            await asyncio.sleep(60)

            # Log stats periodically
            metrics = await collector.collect()
            logger.info(
                f"Resources: CPU {metrics.cpu_percent:.1f}%, "
                f"Memory {metrics.memory_percent:.1f}%, "
                f"GPU {metrics.gpu_utilization_percent:.1f}%"
            )

    except asyncio.CancelledError:
        pass
    finally:
        await collector.stop()


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        asyncio.run(run_collector())
    except KeyboardInterrupt:
        logger.info("Collector stopped by user")
