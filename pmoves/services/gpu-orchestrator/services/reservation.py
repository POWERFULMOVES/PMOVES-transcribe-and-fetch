"""VRAM reservation system for GPU Orchestrator.

Manages VRAM allocation to prevent conflicts when loading multiple models.
Works with RAM tracker to ensure complete resource visibility.
"""

import asyncio
import dataclasses
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class VRAMReservation:
    """A VRAM reservation for a model or workload."""

    reservation_id: str
    gpu_indices: List[int]  # Which GPUs this reservation is for
    reserved_mb: int  # VRAM reserved per GPU
    created_at: datetime
    expires_at: Optional[datetime] = None
    owner: Optional[str] = None  # Service or process that made the reservation
    model_name: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """Check if reservation has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    @property
    def total_reserved_mb(self) -> int:
        """Total VRAM reserved across all GPUs."""
        return self.reserved_mb * len(self.gpu_indices)


@dataclasses.dataclass
class GPUState:
    """Current state of a GPU."""

    index: int
    name: str
    total_mb: int
    used_mb: int
    free_mb: int
    reservations: List[str] = dataclasses.field(default_factory=list)
    reserved_mb: int = 0  # Total VRAM reserved by active reservations

    @property
    def utilization(self) -> float:
        """GPU VRAM utilization (0.0-1.0)."""
        if self.total_mb == 0:
            return 0.0
        return self.used_mb / self.total_mb

    @property
    def available_mb(self) -> int:
        """Available VRAM (free - reserved).

        Returns the amount of VRAM available for new reservations.
        This accounts for both system-used memory and reserved memory.
        """
        return max(0, self.free_mb - self.reserved_mb)


class VRAMReservationManager:
    """Manages VRAM reservations across GPUs.

    Prevents VRAM overcommitment by tracking reservations
    and checking capacity before model loading.
    """

    def __init__(
        self,
        reservation_timeout_seconds: int = 300,  # 5 minutes
        poll_interval_seconds: float = 5.0,
    ):
        """Initialize VRAM reservation manager.

        Args:
            reservation_timeout_seconds: Default timeout for reservations
            poll_interval_seconds: How often to poll GPU state
        """
        self.reservation_timeout = timedelta(seconds=reservation_timeout_seconds)
        self.poll_interval = poll_interval_seconds
        self._reservations: Dict[str, VRAMReservation] = {}
        self._gpu_states: Dict[int, GPUState] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Start background polling of GPU state."""
        if self._running:
            return

        self._running = True
        await self._refresh_gpu_states()
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("VRAM reservation manager started")

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

        logger.info("VRAM reservation manager stopped")

    async def _poll_loop(self):
        """Background polling loop."""
        while self._running:
            try:
                await self._refresh_gpu_states()
                await self._cleanup_expired_reservations()
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
                await asyncio.sleep(self.poll_interval)

    async def _refresh_gpu_states(self):
        """Refresh GPU state from nvidia-smi."""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                [
                    "nvidia-smi",
                    "--query-gpu=index,name,memory.total,memory.used,memory.free",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return

            new_states = {}
            for line in result.stdout.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 5:
                    gpu_id = int(parts[0])
                    name = parts[1]
                    total_mb = int(parts[2])
                    used_mb = int(parts[3])
                    free_mb = int(parts[4])

                    # Preserve reservations from existing state
                    existing = self._gpu_states.get(gpu_id)
                    reservations = existing.reservations if existing else []

                    new_states[gpu_id] = GPUState(
                        index=gpu_id,
                        name=name,
                        total_mb=total_mb,
                        used_mb=used_mb,
                        free_mb=free_mb,
                        reservations=reservations,
                    )

            self._gpu_states = new_states

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            logger.error(
                f"Failed to refresh GPU states: {e}. "
                f"VRAM reservations using stale data - OOM errors may occur."
            )

    async def _cleanup_expired_reservations(self):
        """Remove expired reservations."""
        async with self._lock:
            expired = [
                res_id for res_id, res in self._reservations.items()
                if res.is_expired
            ]

            for res_id in expired:
                await self._release(res_id)

    async def reserve(
        self,
        gpu_indices: List[int],
        required_mb: int,
        owner: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Optional[str]:
        """Reserve VRAM on specified GPUs.

        Args:
            gpu_indices: Which GPUs to reserve on
            required_mb: VRAM required per GPU
            owner: Owner of the reservation
            model_name: Name of model being loaded
            timeout_seconds: Custom timeout (uses default if None)

        Returns:
            Reservation ID if successful, None if insufficient VRAM
        """
        async with self._lock:
            # Check if GPUs exist and have enough VRAM
            for gpu_id in gpu_indices:
                if gpu_id not in self._gpu_states:
                    logger.warning(f"GPU {gpu_id} not found")
                    return None

                gpu = self._gpu_states[gpu_id]
                # Check if required VRAM fits in free space
                if required_mb > gpu.free_mb:
                    logger.warning(
                        f"Insufficient VRAM on GPU {gpu_id}: "
                        f"need {required_mb}MB, have {gpu.free_mb}MB free"
                    )
                    return None

            # Create reservation
            import uuid

            res_id = str(uuid.uuid4())
            expires_at = None
            if timeout_seconds is not None:
                expires_at = datetime.now() + timedelta(seconds=timeout_seconds)
            else:
                expires_at = datetime.now() + self.reservation_timeout

            reservation = VRAMReservation(
                reservation_id=res_id,
                gpu_indices=gpu_indices,
                reserved_mb=required_mb,
                created_at=datetime.now(),
                expires_at=expires_at,
                owner=owner,
                model_name=model_name,
            )

            self._reservations[res_id] = reservation

            # Update GPU states
            for gpu_id in gpu_indices:
                if gpu_id in self._gpu_states:
                    gpu_state = self._gpu_states[gpu_id]
                    gpu_state.reservations.append(res_id)
                    gpu_state.reserved_mb += required_mb

            logger.info(
                f"Reserved {required_mb}MB on GPUs {gpu_indices} "
                f"(reservation: {res_id[:8]}...)"
            )

            return res_id

    async def _release(self, reservation_id: str) -> bool:
        """Release a reservation.

        Args:
            reservation_id: ID of reservation to release

        Returns:
            True if reservation existed and was released
        """
        if reservation_id not in self._reservations:
            return False

        reservation = self._reservations[reservation_id]

        # Remove from GPU states
        for gpu_id in reservation.gpu_indices:
            if gpu_id in self._gpu_states:
                gpu_state = self._gpu_states[gpu_id]
                if reservation_id in gpu_state.reservations:
                    gpu_state.reservations.remove(reservation_id)
                    gpu_state.reserved_mb -= reservation.reserved_mb

        del self._reservations[reservation_id]

        logger.info(f"Released reservation {reservation_id[:8]}...")
        return True

    async def release(self, reservation_id: str) -> bool:
        """Release a reservation (public version with lock)."""
        async with self._lock:
            return await self._release(reservation_id)

    async def can_fit(
        self,
        required_mb: int,
        gpu_count: int = 1,
        prefer_nvlink: bool = True,
    ) -> Optional[List[int]]:
        """Check if a workload can fit and return best GPUs.

        Args:
            required_mb: VRAM required per GPU
            gpu_count: Number of GPUs needed
            prefer_nvlink: Prefer NVLink-connected GPUs

        Returns:
            List of GPU indices if workload can fit, None otherwise
        """
        async with self._lock:
            # Group GPUs by availability and NVLink topology
            available_gpus = []

            for gpu_id, state in self._gpu_states.items():
                if state.free_mb >= required_mb:
                    available_gpus.append(gpu_id)

            if len(available_gpus) < gpu_count:
                return None

            # If we need multiple GPUs, try to find NVLink-connected ones
            if gpu_count > 1 and prefer_nvlink:
                nvlink_groups = self._find_nvlink_groups(
                    available_gpus, gpu_count
                )
                if nvlink_groups:
                    return nvlink_groups[0]  # Return first suitable group

            # Otherwise, return first available GPUs
            return available_gpus[:gpu_count]

    def _find_nvlink_groups(
        self,
        available_gpus: List[int],
        group_size: int,
    ) -> List[List[int]]:
        """Find groups of potentially NVLink-connected GPUs.

        NOTE: Current implementation uses sequential GPU indices as a heuristic
        since true NVLink topology detection is not yet implemented. This
        assumes GPUs are ordered consecutively on the PCIe/NVLink fabric.

        True NVLink topology detection would require querying hardware
        topology from nvidia-smi or pynvml.

        Args:
            available_gpus: Available GPU indices
            group_size: Desired group size

        Returns:
            List of GPU groups with consecutive indices (heuristic for NVLink)
        """
        # This would require NVLink topology info from hardware detection
        # For now, return sequential GPUs as a simple heuristic
        if len(available_gpus) < group_size:
            return []

        groups = []
        # Assume GPUs are grouped sequentially (0,1,2,3, etc.)
        for i in range(0, len(available_gpus) - group_size + 1):
            group = available_gpus[i:i + group_size]
            # Check if indices are consecutive
            if all(group[j] + 1 == group[j + 1] for j in range(len(group) - 1)):
                groups.append(group)

        return groups

    def get_reservation(self, reservation_id: str) -> Optional[VRAMReservation]:
        """Get reservation by ID.

        Args:
            reservation_id: Reservation ID

        Returns:
            VRAMReservation if found, None otherwise
        """
        return self._reservations.get(reservation_id)

    def list_reservations(
        self,
        owner: Optional[str] = None,
        active_only: bool = False,
    ) -> List[VRAMReservation]:
        """List reservations with optional filtering.

        Args:
            owner: Filter by owner
            active_only: Only include non-expired reservations

        Returns:
            List of VRAMReservations
        """
        reservations = list(self._reservations.values())

        if owner:
            reservations = [r for r in reservations if r.owner == owner]

        if active_only:
            reservations = [r for r in reservations if not r.is_expired]

        return reservations

    def get_gpu_states(self) -> Dict[int, GPUState]:
        """Get current GPU states.

        Returns:
            Dict mapping GPU index to GPUState
        """
        return self._gpu_states.copy()

    def get_stats(self) -> Dict:
        """Get manager statistics.

        Returns:
            Dict with stats
        """
        total_reservations = len(self._reservations)
        active_reservations = sum(
            1 for r in self._reservations.values() if not r.is_expired
        )
        total_reserved_mb = sum(
            r.total_reserved_mb for r in self._reservations.values()
            if not r.is_expired
        )

        gpu_stats = {
            gpu_id: {
                "total_mb": state.total_mb,
                "used_mb": state.used_mb,
                "free_mb": state.free_mb,
                "utilization": round(state.utilization, 3),
                "reservations": len(state.reservations),
            }
            for gpu_id, state in self._gpu_states.items()
        }

        return {
            "status": "running" if self._running else "stopped",
            "total_reservations": total_reservations,
            "active_reservations": active_reservations,
            "total_reserved_mb": total_reserved_mb,
            "gpus": gpu_stats,
        }


async def run_manager(
    reservation_timeout_seconds: int = 300,
    poll_interval_seconds: float = 5.0,
):
    """Run VRAM reservation manager as standalone service.

    Args:
        reservation_timeout_seconds: Default reservation timeout
        poll_interval_seconds: State polling interval
    """
    manager = VRAMReservationManager(
        reservation_timeout_seconds=reservation_timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
    )

    await manager.start()

    try:
        # Keep running
        while True:
            await asyncio.sleep(1)

            # Log stats periodically
            stats = manager.get_stats()
            logger.info(f"Reservations: {stats['active_reservations']} active, "
                       f"{stats['total_reserved_mb']}MB reserved")

    except asyncio.CancelledError:
        pass
    finally:
        await manager.stop()


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        asyncio.run(run_manager())
    except KeyboardInterrupt:
        logger.info("Manager stopped by user")
