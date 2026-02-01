"""System RAM tracking for GPU Orchestrator.

Monitors system memory usage to prevent OOM when loading large models.
Works alongside VRAM tracking to ensure complete resource visibility.
"""

import asyncio
import dataclasses
import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class MemorySnapshot:
    """Snapshot of system and GPU memory at a point in time."""

    timestamp: datetime

    # System memory
    system_total_mb: int
    system_used_mb: int
    system_available_mb: int
    system_buffers_mb: int
    system_cached_mb: int

    # GPU memory (if available)
    gpu_total_mb: int = 0
    gpu_used_mb: int = 0
    gpu_free_mb: int = 0

    @property
    def system_utilization(self) -> float:
        """System memory utilization (0.0-1.0)."""
        if self.system_total_mb == 0:
            return 0.0
        return self.system_used_mb / self.system_total_mb

    @property
    def gpu_utilization(self) -> float:
        """GPU memory utilization (0.0-1.0)."""
        if self.gpu_total_mb == 0:
            return 0.0
        return self.gpu_used_mb / self.gpu_total_mb

    @property
    def can_fit_model(self, model_ram_mb: int, safety_margin: float = 0.1) -> bool:
        """Check if model can fit in available system RAM.

        Args:
            model_ram_mb: Model size in MB
            safety_margin: Additional safety margin (default 10%)

        Returns:
            True if model can fit
        """
        available = self.system_available_mb - (model_ram_mb * safety_margin)
        return available >= 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "system": {
                "total_mb": self.system_total_mb,
                "used_mb": self.system_used_mb,
                "available_mb": self.system_available_mb,
                "utilization": round(self.system_utilization, 3),
            },
            "gpu": {
                "total_mb": self.gpu_total_mb,
                "used_mb": self.gpu_used_mb,
                "free_mb": self.gpu_free_mb,
                "utilization": round(self.gpu_utilization, 3),
            } if self.gpu_total_mb > 0 else None,
        }


class SystemRamTracker:
    """Track system RAM usage for model loading decisions.

    Provides real-time memory monitoring and prediction for
    safe model loading without OOM conditions.
    """

    def __init__(
        self,
        poll_interval_seconds: float = 5.0,
        history_size: int = 60,
    ):
        """Initialize RAM tracker.

        Args:
            poll_interval_seconds: How often to poll memory stats
            history_size: Number of snapshots to keep in history
        """
        self.poll_interval = poll_interval_seconds
        self.history_size = history_size
        self._history: List[MemorySnapshot] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def get_snapshot(self) -> MemorySnapshot:
        """Get current memory snapshot.

        Returns:
            MemorySnapshot with current system and GPU memory
        """
        # Read /proc/meminfo for system memory
        system_info = await self._read_meminfo()

        # Try to get GPU memory from nvidia-smi
        gpu_info = await self._read_gpu_memory()

        return MemorySnapshot(
            timestamp=datetime.now(),
            system_total_mb=system_info["MemTotal"],
            system_used_mb=system_info["MemUsed"],
            system_available_mb=system_info["MemAvailable"],
            system_buffers_mb=system_info["Buffers"],
            system_cached_mb=system_info["Cached"],
            gpu_total_mb=gpu_info["total_mb"],
            gpu_used_mb=gpu_info["used_mb"],
            gpu_free_mb=gpu_info["free_mb"],
        )

    async def _read_meminfo(self) -> Dict[str, int]:
        """Read /proc/meminfo for system memory stats.

        Returns:
            Dict with memory values in MB
        """
        try:
            content = await asyncio.to_thread(Path("/proc/meminfo").read_text)

            meminfo = {}
            for line in content.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    # Parse value like "12345 kB"
                    match = re.search(r"(\d+)\s*kB", value)
                    if match:
                        # Convert KB to MB
                        meminfo[key] = int(match.group(1)) // 1024

            # Calculate derived values
            total = meminfo.get("MemTotal", 0)
            mem_free = meminfo.get("MemFree", 0)
            buffers = meminfo.get("Buffers", 0)
            cached = meminfo.get("Cached", 0) + meminfo.get("SReclaimable", 0)
            available = meminfo.get("MemAvailable", mem_free + buffers + cached)
            used = total - available

            return {
                "MemTotal": total,
                "MemUsed": used,
                "MemAvailable": available,
                "MemFree": mem_free,
                "Buffers": buffers,
                "Cached": cached,
            }

        except (OSError, ValueError) as e:
            logger.error(
                f"Critical: Cannot read system memory from /proc/meminfo: {e}. "
                f"RAM tracking is DISABLED - cannot safely determine model loading capacity."
            )
            # Raise instead of returning fake values - this is a critical failure
            raise RuntimeError(
                f"Memory detection failed - cannot read /proc/meminfo: {e}"
            ) from e

    async def _read_gpu_memory(self) -> Dict[str, int]:
        """Read GPU memory from nvidia-smi.

        Returns:
            Dict with GPU memory values in MB
        """
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["nvidia-smi", "--query-gpu=memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return {"total_mb": 0, "used_mb": 0, "free_mb": 0}

            # Sum across all GPUs
            total_mb = 0
            used_mb = 0
            free_mb = 0

            for line in result.stdout.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    total_mb += int(parts[0])
                    used_mb += int(parts[1])
                    free_mb += int(parts[2])

            return {"total_mb": total_mb, "used_mb": used_mb, "free_mb": free_mb}

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            logger.warning(
                f"GPU memory detection unavailable: {e}. "
                f"VRAM tracking disabled - GPU models may fail to load."
            )
            return {"total_mb": 0, "used_mb": 0, "free_mb": 0}

    async def start(self):
        """Start background polling of memory stats."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("RAM tracker started")

    async def stop(self):
        """Stop background polling."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("RAM tracker stopped")

    async def _poll_loop(self):
        """Background polling loop."""
        while self._running:
            try:
                snapshot = await self.get_snapshot()
                self._history.append(snapshot)

                # Keep history bounded
                if len(self._history) > self.history_size:
                    self._history.pop(0)

                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
                await asyncio.sleep(self.poll_interval)

    def get_history(self) -> List[MemorySnapshot]:
        """Get memory history.

        Returns:
            List of recent snapshots
        """
        return self._history.copy()

    def get_trend(self, window_seconds: float = 30.0) -> Dict[str, float]:
        """Analyze memory usage trend.

        Args:
            window_seconds: Time window to analyze

        Returns:
            Dict with trend metrics
        """
        if len(self._history) < 2:
            return {"trend_mb_per_sec": 0.0, "predicted_oom_seconds": None}

        # Get snapshots within window
        now = datetime.now()
        window_snapshots = [
            s for s in self._history
            if (now - s.timestamp).total_seconds() <= window_seconds
        ]

        if len(window_snapshots) < 2:
            return {"trend_mb_per_sec": 0.0, "predicted_oom_seconds": None}

        # Calculate linear regression slope
        first = window_snapshots[0]
        last = window_snapshots[-1]
        time_diff = (last.timestamp - first.timestamp).total_seconds()

        if time_diff <= 0:
            return {"trend_mb_per_sec": 0.0, "predicted_oom_seconds": None}

        usage_diff = last.system_used_mb - first.system_used_mb
        trend_mb_per_sec = usage_diff / time_diff

        # Predict OOM if trend is positive
        predicted_oom_seconds = None
        if trend_mb_per_sec > 0:
            remaining_mb = last.system_available_mb
            predicted_oom_seconds = remaining_mb / trend_mb_per_sec

        return {
            "trend_mb_per_sec": trend_mb_per_sec,
            "predicted_oom_seconds": predicted_oom_seconds,
        }

    async def estimate_model_memory(
        self,
        model_params: int,
        quantization_bits: int = 16,
        context_length: int = 4096,
    ) -> int:
        """Estimate model memory requirements in MB.

        Args:
            model_params: Number of parameters
            quantization_bits: Bits per parameter (4, 8, 16)
            context_length: Context length for KV cache

        Returns:
            Estimated memory in MB
        """
        # Model weights memory
        weights_bytes = (model_params * quantization_bits) // 8
        weights_mb = weights_bytes // (1024 * 1024)

        # KV cache estimation (rough approximation)
        # 2 bytes per token per layer, assume ~32 layers for 7B model
        layers = max(32, model_params // 1_000_000_000 * 4)
        kv_cache_bytes = context_length * layers * 2 * quantization_bits // 8
        kv_cache_mb = kv_cache_bytes // (1024 * 1024)

        # Activation memory (rough estimate, typically 20-30% of weights)
        activation_mb = int(weights_mb * 0.25)

        # Overhead for optimizer state (if training)
        # For inference, this is minimal

        total_mb = weights_mb + kv_cache_mb + activation_mb

        logger.debug(
            f"Model memory estimate: {total_mb}MB "
            f"(weights: {weights_mb}MB, KV: {kv_cache_mb}MB, activation: {activation_mb}MB)"
        )

        return total_mb

    async def can_load_model(
        self,
        model_params: int,
        quantization_bits: int = 16,
        context_length: int = 4096,
        safety_margin: float = 0.15,
    ) -> tuple[bool, str]:
        """Check if model can be loaded safely.

        Args:
            model_params: Number of parameters
            quantization_bits: Bits per parameter
            context_length: Context length
            safety_margin: Safety margin (default 15%)

        Returns:
            Tuple of (can_load, reason)
        """
        snapshot = await self.get_snapshot()
        estimated_mb = await self.estimate_model_memory(
            model_params, quantization_bits, context_length
        )

        required_mb = int(estimated_mb * (1 + safety_margin))
        available_mb = snapshot.system_available_mb

        if snapshot.gpu_total_mb > 0:
            # We have GPU - check if model fits in GPU
            if estimated_mb > snapshot.gpu_total_mb:
                return False, f"Model requires {estimated_mb}MB VRAM, only {snapshot.gpu_total_mb}MB available"

            # Check system RAM for offloaded portions
            if required_mb > available_mb:
                return False, f"Model requires {required_mb}MB system RAM, only {available_mb}MB available"

        else:
            # CPU-only - check system RAM
            if required_mb > available_mb:
                return False, f"Model requires {required_mb}MB system RAM, only {available_mb}MB available"

        # Check trend for potential OOM
        trend = self.get_trend()
        if trend["predicted_oom_seconds"] is not None and trend["predicted_oom_seconds"] < 300:
            return False, f"System trending toward OOM in {trend['predicted_oom_seconds']:.0f}s"

        return True, f"Model can be loaded (requires {required_mb}MB, {available_mb}MB available)"

    def get_stats(self) -> Dict:
        """Get current tracker statistics.

        Returns:
            Dict with stats
        """
        if not self._history:
            return {"status": "no_data"}

        latest = self._history[-1]
        trend = self.get_trend()

        return {
            "status": "running" if self._running else "stopped",
            "history_size": len(self._history),
            "latest": latest.to_dict(),
            "trend": {
                "mb_per_sec": round(trend["trend_mb_per_sec"], 2),
                "predicted_oom_seconds": trend["predicted_oom_seconds"],
            },
        }


async def run_tracker(
    poll_interval_seconds: float = 5.0,
    history_size: int = 60,
):
    """Run RAM tracker as standalone service.

    Args:
        poll_interval_seconds: Polling interval
        history_size: History buffer size
    """
    tracker = SystemRamTracker(poll_interval_seconds, history_size)

    await tracker.start()

    try:
        # Keep running
        while True:
            await asyncio.sleep(1)

            # Log stats periodically
            stats = tracker.get_stats()
            if "latest" in stats:
                logger.info(f"RAM: {stats['latest']['system']['used_mb']}MB / "
                           f"{stats['latest']['system']['total_mb']}MB "
                           f"({stats['latest']['system']['utilization']:.1%})")

    except asyncio.CancelledError:
        pass
    finally:
        await tracker.stop()


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        asyncio.run(run_tracker())
    except KeyboardInterrupt:
        logger.info("Tracker stopped by user")
