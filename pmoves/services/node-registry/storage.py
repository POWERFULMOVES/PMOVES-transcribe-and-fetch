"""Storage backend for node registry.

Supports in-memory and Supabase backends for node capability storage.
"""

import dataclasses
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from ..resource_detector.models import NodeCapabilities, NodeHeartbeat

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class NodeRecord:
    """Stored node record with metadata."""

    capabilities: NodeCapabilities
    registered_at: datetime
    last_heartbeat: datetime
    heartbeat_count: int = 0
    status: str = "online"  # online, busy, draining, offline

    @property
    def is_stale(self) -> bool:
        """Check if node record is stale (no recent heartbeat)."""
        return datetime.now() - self.last_heartbeat > timedelta(seconds=60)

    @property
    def is_offline(self) -> bool:
        """Check if node should be considered offline."""
        return datetime.now() - self.last_heartbeat > timedelta(seconds=120)


class InMemoryNodeStore:
    """In-memory storage for node registry.

    Fast, ephemeral storage suitable for single-host deployments.
    Data is lost on restart.
    """

    def __init__(self, stale_threshold_seconds: int = 60):
        """Initialize in-memory store.

        Args:
            stale_threshold_seconds: Seconds before a node is considered stale
        """
        self._nodes: Dict[str, NodeRecord] = {}
        self._by_tier: Dict[str, Set[str]] = {}  # tier -> node_ids
        self._stale_threshold = timedelta(seconds=stale_threshold_seconds)

    async def register(self, capabilities: NodeCapabilities) -> NodeRecord:
        """Register a new node or update existing.

        Args:
            capabilities: Node capabilities from announcement

        Returns:
            Created or updated NodeRecord
        """
        now = datetime.now()
        node_id = capabilities.node_id

        if node_id in self._nodes:
            # Update existing node
            record = self._nodes[node_id]
            record.capabilities = capabilities
            record.last_heartbeat = now
            record.status = "online"
        else:
            # New node registration
            record = NodeRecord(
                capabilities=capabilities,
                registered_at=now,
                last_heartbeat=now,
                heartbeat_count=0,
                status="online",
            )
            self._nodes[node_id] = record

            # Index by tier
            tier = capabilities.tier.value
            if tier not in self._by_tier:
                self._by_tier[tier] = set()
            self._by_tier[tier].add(node_id)

        logger.info(f"Node registered: {node_id} ({capabilities.tier.value})")
        return record

    async def get(self, node_id: str) -> Optional[NodeRecord]:
        """Get node record by ID.

        Args:
            node_id: Node identifier

        Returns:
            NodeRecord if found, None otherwise
        """
        return self._nodes.get(node_id)

    async def list_all(self) -> List[NodeRecord]:
        """List all node records.

        Returns:
            List of all NodeRecords
        """
        return list(self._nodes.values())

    async def list_by_tier(self, tier: str) -> List[NodeRecord]:
        """List nodes by tier.

        Args:
            tier: Node tier value (e.g., "ai_factory", "gpu_peer")

        Returns:
            List of NodeRecords for the tier
        """
        node_ids = self._by_tier.get(tier, set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]

    async def list_online(self) -> List[NodeRecord]:
        """List only online (non-stale) nodes.

        Returns:
            List of online NodeRecords
        """
        now = datetime.now()
        return [
            record
            for record in self._nodes.values()
            if now - record.last_heartbeat <= self._stale_threshold
        ]

    async def update_heartbeat(self, heartbeat: NodeHeartbeat) -> Optional[NodeRecord]:
        """Update node from heartbeat.

        Args:
            heartbeat: Heartbeat message from node

        Returns:
            Updated NodeRecord if found, None otherwise
        """
        record = await self.get(heartbeat.node_id)
        if record is None:
            return None

        record.last_heartbeat = heartbeat.timestamp
        record.heartbeat_count += 1
        record.status = heartbeat.status

        # Update dynamic capability fields
        record.capabilities.available_cpu_slots = (
            record.capabilities.cpu.total_threads - int(record.capabilities.cpu.total_threads * heartbeat.cpu_utilization)
        )
        record.capabilities.available_memory_mb = int(
            record.capabilities.memory.total_mb * (1 - heartbeat.memory_utilization)
        )

        return record

    async def mark_offline(self, node_id: str) -> bool:
        """Mark a node as offline.

        Args:
            node_id: Node identifier

        Returns:
            True if node was found and marked offline
        """
        record = await self.get(node_id)
        if record is None:
            return False

        record.status = "offline"
        logger.info(f"Node marked offline: {node_id}")
        return True

    async def remove(self, node_id: str) -> bool:
        """Remove a node from registry.

        Args:
            node_id: Node identifier

        Returns:
            True if node was found and removed
        """
        record = await self.get(node_id)
        if record is None:
            return False

        # Remove from tier index
        tier = record.capabilities.tier.value
        if tier in self._by_tier and node_id in self._by_tier[tier]:
            self._by_tier[tier].remove(node_id)

        # Remove from main store
        del self._nodes[node_id]
        logger.info(f"Node removed: {node_id}")
        return True

    async def cleanup_stale(self) -> int:
        """Remove stale nodes from registry.

        Returns:
            Number of nodes removed
        """
        now = datetime.now()
        stale_ids = [
            node_id
            for node_id, record in self._nodes.items()
            if now - record.last_heartbeat > self._stale_threshold
        ]

        for node_id in stale_ids:
            await self.remove(node_id)

        if stale_ids:
            logger.info(f"Cleaned up {len(stale_ids)} stale nodes")

        return len(stale_ids)

    async def query(
        self,
        tier: Optional[str] = None,
        min_cpu: Optional[int] = None,
        min_ram_mb: Optional[int] = None,
        requires_gpu: bool = False,
        online_only: bool = True,
    ) -> List[NodeRecord]:
        """Query nodes with filters.

        Args:
            tier: Filter by tier (if specified)
            min_cpu: Minimum available CPU slots
            min_ram_mb: Minimum available RAM in MB
            requires_gpu: Only return nodes with GPU available
            online_only: Only return online (non-stale) nodes

        Returns:
            List of matching NodeRecords
        """
        records = await self.list_online() if online_only else await self.list_all()

        if tier:
            records = [r for r in records if r.capabilities.tier.value == tier]

        if min_cpu:
            records = [r for r in records if r.capabilities.available_cpu_slots >= min_cpu]

        if min_ram_mb:
            records = [r for r in records if r.capabilities.available_memory_mb >= min_ram_mb]

        if requires_gpu:
            records = [r for r in records if r.capabilities.available_gpu_slots > 0]

        return records

    def get_stats(self) -> Dict:
        """Get registry statistics.

        Returns:
            Dictionary with stats
        """
        now = datetime.now()
        total = len(self._nodes)
        online = sum(
            1 for r in self._nodes.values() if now - r.last_heartbeat <= self._stale_threshold
        )
        by_tier = {
            tier: len(nodes)
            for tier, nodes in self._by_tier.items()
        }

        return {
            "total_nodes": total,
            "online_nodes": online,
            "offline_nodes": total - online,
            "by_tier": by_tier,
        }


class SupabaseNodeStore(InMemoryNodeStore):
    """Supabase-backed storage for node registry.

    Provides persistent storage with Supabase as backend.
    Falls back to in-memory for reads if Supabase is unavailable.
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        stale_threshold_seconds: int = 60,
    ):
        """Initialize Supabase store.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service key
            stale_threshold_seconds: Seconds before a node is considered stale
        """
        super().__init__(stale_threshold_seconds)
        self._supabase_url = supabase_url
        self._supabase_key = supabase_key
        self._table_name = "compute_nodes"
        self._client: Optional[Any] = None

    async def _get_client(self):
        """Lazy-load Supabase client."""
        if self._client is not None:
            return self._client

        try:
            from supabase import create_client

            self._client = create_client(self._supabase_url, self._supabase_key)
            return self._client
        except ImportError:
            logger.warning("Supabase client not available, using in-memory only")
            return None
        except Exception as e:
            logger.warning(f"Failed to create Supabase client: {e}")
            return None

    async def _persist_to_supabase(self, record: NodeRecord):
        """Persist record to Supabase.

        Args:
            record: NodeRecord to persist
        """
        client = await self._get_client()
        if client is None:
            return

        try:
            data = {
                "node_id": record.capabilities.node_id,
                "hostname": record.capabilities.hostname,
                "tier": record.capabilities.tier.value,
                "cpu_cores": record.capabilities.cpu.cores,
                "cpu_threads": record.capabilities.cpu.total_threads,
                "memory_gb": record.capabilities.memory.total_gb,
                "gpu_count": len(record.capabilities.gpus),
                "gpu_vram_gb": record.capabilities.total_gpu_vram_gb,
                "ipv4": record.capabilities.ipv4,
                "available_cpu_slots": record.capabilities.available_cpu_slots,
                "available_gpu_slots": record.capabilities.available_gpu_slots,
                "available_memory_mb": record.capabilities.available_memory_mb,
                "status": record.status,
                "last_heartbeat": record.last_heartbeat.isoformat(),
                "registered_at": record.registered_at.isoformat(),
                "heartbeat_count": record.heartbeat_count,
            }

            # Upsert to Supabase
            client.table(self._table_name).upsert(data, on_conflict="node_id").execute()

        except Exception as e:
            logger.warning(f"Failed to persist to Supabase: {e}")

    async def register(self, capabilities: NodeCapabilities) -> NodeRecord:
        """Register node with Supabase persistence."""
        record = await super().register(capabilities)
        await self._persist_to_supabase(record)
        return record

    async def update_heartbeat(self, heartbeat: NodeHeartbeat) -> Optional[NodeRecord]:
        """Update heartbeat with Supabase persistence."""
        record = await super().update_heartbeat(heartbeat)
        if record:
            await self._persist_to_supabase(record)
        return record
