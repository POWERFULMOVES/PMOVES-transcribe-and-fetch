import asyncio
import psutil
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends

router = APIRouter()

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self._running = False

    def add_metric(self, name: str, value: float):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def get_metrics(self) -> Dict[str, Any]:
        result = {}
        for name, values in self.metrics.items():
            if values:
                result[name] = {
                    'current': values[-1],
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        return result

    async def collect_system_metrics(self):
        self._running = True
        while self._running:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            self.add_metric('cpu_usage', cpu_percent)
            self.add_metric('memory_usage', memory.percent)
            
            await asyncio.sleep(5)  # Collect every 5 seconds

    def stop(self):
        self._running = False

class TranscriptionMetrics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.active_connections = 0
        self.start_time = datetime.now()

    def record_request(self, success: bool):
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

    def connection_started(self):
        self.active_connections += 1

    def connection_ended(self):
        self.active_connections = max(0, self.active_connections - 1)

    def get_metrics(self) -> Dict[str, Any]:
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'active_connections': self.active_connections,
            'uptime_seconds': uptime,
            'success_rate': (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        }

# Global instances for state management
_metrics_collector = MetricsCollector()
_transcription_metrics = TranscriptionMetrics()

def get_metrics_collector():
    return _metrics_collector

def get_transcription_metrics():
    return _transcription_metrics

@router.get("/metrics")
async def get_metrics(
    metrics_collector: MetricsCollector = Depends(get_metrics_collector),
    transcription_metrics: TranscriptionMetrics = Depends(get_transcription_metrics)
) -> Dict[str, Dict[str, Any]]:
    return {
        'system': metrics_collector.get_metrics(),
        'transcription': transcription_metrics.get_metrics()
    } 