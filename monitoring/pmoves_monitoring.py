"""
PMOVES Monitoring Integration

This module provides comprehensive monitoring capabilities for the PMOVES platform:
- Prometheus metrics collection
- Langfuse LLM observability with @observe decorator
- Structured logging with correlation IDs
- Performance tracking and alerting
- Health checks and status monitoring

Usage:
    from monitoring.pmoves_monitoring import PMOVESMonitoring

    monitor = PMOVESMonitoring(service_name="pmoves-backend")

    # Track metrics
    monitor.track_request("api_call", duration=0.5, status="success")

    # Use @observe decorator for LLM tracing
    @observe()
    def my_llm_function():
        return openai.chat.completions.create(...)

    # Log with correlation
    monitor.log_info("Processing request", request_id="req-123", user_id="user-456")
"""

import os
import time
import uuid
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from functools import wraps

import structlog
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
)
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import openai  # Use Langfuse OpenAI integration
import redis.asyncio as redis


@dataclass
class MetricData:
    """Data structure for metric collection"""

    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    metric_type: str  # counter, histogram, gauge


@dataclass
class TraceData:
    """Data structure for trace information"""

    trace_id: str
    span_id: str
    operation: str
    service: str
    duration: Optional[float] = None
    status: str = "success"
    metadata: Dict[str, Any] = None
    parent_span_id: Optional[str] = None


class PMOVESMonitoring:
    """Comprehensive monitoring for PMOVES services"""

    def __init__(
        self,
        service_name: str,
        langfuse_public_key: Optional[str] = None,
        langfuse_secret_key: Optional[str] = None,
        langfuse_host: Optional[str] = None,
        redis_url: Optional[str] = None,
        enable_prometheus: bool = True,
        enable_langfuse: bool = True,
        enable_structured_logging: bool = True,
    ):
        self.service_name = service_name
        self.enable_prometheus = enable_prometheus
        self.enable_langfuse = enable_langfuse
        self.enable_structured_logging = enable_structured_logging

        # Initialize components
        self._init_prometheus()
        self._init_langfuse(langfuse_public_key, langfuse_secret_key, langfuse_host)
        self._init_structured_logging()
        self._init_redis(redis_url)

        # Correlation tracking
        self.current_trace_id = None
        self.current_span_id = None

    def _init_prometheus(self):
        """Initialize Prometheus metrics"""
        if not self.enable_prometheus:
            return

        self.registry = CollectorRegistry()

        # Core metrics
        self.request_counter = Counter(
            "pmoves_requests_total",
            "Total number of requests",
            ["service", "endpoint", "method", "status"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "pmoves_request_duration_seconds",
            "Request duration in seconds",
            ["service", "endpoint", "method"],
            registry=self.registry,
        )

        self.active_connections = Gauge(
            "pmoves_active_connections",
            "Number of active connections",
            ["service"],
            registry=self.registry,
        )

        # LLM-specific metrics
        self.llm_requests = Counter(
            "pmoves_llm_requests_total",
            "Total LLM requests",
            ["service", "provider", "model", "status"],
            registry=self.registry,
        )

        self.llm_duration = Histogram(
            "pmoves_llm_duration_seconds",
            "LLM request duration",
            ["service", "provider", "model"],
            registry=self.registry,
        )

        self.llm_tokens = Counter(
            "pmoves_llm_tokens_total",
            "Total tokens used",
            ["service", "provider", "model", "type"],
            registry=self.registry,
        )

        self.llm_cost = Counter(
            "pmoves_llm_cost_total",
            "Total LLM cost in USD",
            ["service", "provider", "model"],
            registry=self.registry,
        )

        # Agent-specific metrics
        self.agent_operations = Counter(
            "pmoves_agent_operations_total",
            "Total agent operations",
            ["service", "agent_type", "operation", "status"],
            registry=self.registry,
        )

        self.agent_response_time = Histogram(
            "pmoves_agent_response_seconds",
            "Agent response time",
            ["service", "agent_type", "operation"],
            registry=self.registry,
        )

        # Search and content metrics
        self.search_requests = Counter(
            "pmoves_search_requests_total",
            "Total search requests",
            ["service", "search_type", "status"],
            registry=self.registry,
        )

        self.search_duration = Histogram(
            "pmoves_search_duration_seconds",
            "Search duration",
            ["service", "search_type"],
            registry=self.registry,
        )

        self.content_processing = Counter(
            "pmoves_content_processing_total",
            "Content processing operations",
            ["service", "content_type", "operation", "status"],
            registry=self.registry,
        )

        # Error tracking
        self.error_counter = Counter(
            "pmoves_errors_total",
            "Total errors",
            ["service", "error_type", "severity"],
            registry=self.registry,
        )

        # Rate limiting metrics
        self.rate_limit_hits = Counter(
            "pmoves_rate_limit_hits_total",
            "Rate limit violations",
            ["service", "endpoint", "user_id"],
            registry=self.registry,
        )

    def _init_langfuse(
        self, public_key: Optional[str], secret_key: Optional[str], host: Optional[str]
    ):
        """Initialize Langfuse for LLM observability using the decorator approach"""
        if not self.enable_langfuse:
            return

        try:
            # Configure Langfuse context for decorators
            langfuse_context.configure(
                public_key=public_key or os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=secret_key or os.getenv("LANGFUSE_SECRET_KEY"),
                host=host or os.getenv("LANGFUSE_HOST", "http://localhost:3002"),
                enabled=True,
                debug=os.getenv("LANGFUSE_DEBUG", "False").lower() == "true",
            )

            # Also create a client for manual operations
            self.langfuse = Langfuse(
                public_key=public_key or os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=secret_key or os.getenv("LANGFUSE_SECRET_KEY"),
                host=host or os.getenv("LANGFUSE_HOST", "http://localhost:3002"),
            )
            self.langfuse_enabled = True

        except Exception as e:
            logging.warning(f"Failed to initialize Langfuse: {e}")
            self.langfuse_enabled = False

    def _init_structured_logging(self):
        """Initialize structured logging"""
        if not self.enable_structured_logging:
            return

        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        self.logger = structlog.get_logger(self.service_name)

    def _init_redis(self, redis_url: Optional[str]):
        """Initialize Redis for caching and coordination"""
        try:
            self.redis_client = redis.from_url(
                redis_url or os.getenv("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True,
            )
        except Exception as e:
            logging.warning(f"Failed to initialize Redis: {e}")
            self.redis_client = None

    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID"""
        return f"{self.service_name}-{uuid.uuid4().hex[:8]}"

    def set_trace_context(self, trace_id: str, span_id: Optional[str] = None):
        """Set the current trace context"""
        self.current_trace_id = trace_id
        self.current_span_id = span_id or self.generate_correlation_id()

    def get_trace_context(self) -> Dict[str, str]:
        """Get the current trace context"""
        return {
            "trace_id": self.current_trace_id,
            "span_id": self.current_span_id,
            "service": self.service_name,
        }

    # Prometheus Metrics Methods
    def track_request(
        self,
        endpoint: str,
        method: str = "GET",
        status: str = "success",
        duration: Optional[float] = None,
    ):
        """Track HTTP request metrics"""
        if not self.enable_prometheus:
            return

        status_code = (
            "2xx" if status == "success" else "5xx" if status == "error" else "4xx"
        )

        self.request_counter.labels(
            service=self.service_name,
            endpoint=endpoint,
            method=method,
            status=status_code,
        ).inc()

        if duration is not None:
            self.request_duration.labels(
                service=self.service_name, endpoint=endpoint, method=method
            ).observe(duration)

    def track_llm_call(
        self,
        provider: str,
        model: str,
        status: str = "success",
        duration: Optional[float] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
    ):
        """Track LLM call metrics"""
        if not self.enable_prometheus:
            return

        self.llm_requests.labels(
            service=self.service_name, provider=provider, model=model, status=status
        ).inc()

        if duration is not None:
            self.llm_duration.labels(
                service=self.service_name, provider=provider, model=model
            ).observe(duration)

        if input_tokens > 0:
            self.llm_tokens.labels(
                service=self.service_name, provider=provider, model=model, type="input"
            ).inc(input_tokens)

        if output_tokens > 0:
            self.llm_tokens.labels(
                service=self.service_name, provider=provider, model=model, type="output"
            ).inc(output_tokens)

        if cost > 0:
            self.llm_cost.labels(
                service=self.service_name, provider=provider, model=model
            ).inc(cost)

    def track_agent_operation(
        self,
        agent_type: str,
        operation: str,
        status: str = "success",
        duration: Optional[float] = None,
    ):
        """Track agent operation metrics"""
        if not self.enable_prometheus:
            return

        self.agent_operations.labels(
            service=self.service_name,
            agent_type=agent_type,
            operation=operation,
            status=status,
        ).inc()

        if duration is not None:
            self.agent_response_time.labels(
                service=self.service_name, agent_type=agent_type, operation=operation
            ).observe(duration)

    def track_search(
        self,
        search_type: str,
        status: str = "success",
        duration: Optional[float] = None,
    ):
        """Track search operation metrics"""
        if not self.enable_prometheus:
            return

        self.search_requests.labels(
            service=self.service_name, search_type=search_type, status=status
        ).inc()

        if duration is not None:
            self.search_duration.labels(
                service=self.service_name, search_type=search_type
            ).observe(duration)

    def track_content_processing(
        self, content_type: str, operation: str, status: str = "success"
    ):
        """Track content processing metrics"""
        if not self.enable_prometheus:
            return

        self.content_processing.labels(
            service=self.service_name,
            content_type=content_type,
            operation=operation,
            status=status,
        ).inc()

    def track_error(self, error_type: str, severity: str = "error"):
        """Track error metrics"""
        if not self.enable_prometheus:
            return

        self.error_counter.labels(
            service=self.service_name, error_type=error_type, severity=severity
        ).inc()

    def track_rate_limit_hit(self, endpoint: str, user_id: str = "anonymous"):
        """Track rate limit violations"""
        if not self.enable_prometheus:
            return

        self.rate_limit_hits.labels(
            service=self.service_name, endpoint=endpoint, user_id=user_id
        ).inc()

    def set_active_connections(self, count: int):
        """Set the number of active connections"""
        if not self.enable_prometheus:
            return

        self.active_connections.labels(service=self.service_name).set(count)

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        if not self.enable_prometheus:
            return ""
        return generate_latest(self.registry).decode("utf-8")

    # Langfuse Integration Methods
    def get_current_trace_url(self) -> Optional[str]:
        """Get the URL of the current trace"""
        if not self.langfuse_enabled:
            return None
        try:
            return langfuse_context.get_current_trace_url()
        except Exception as e:
            self.log_error("Failed to get trace URL", error=str(e))
            return None

    def get_current_trace_id(self) -> Optional[str]:
        """Get the current trace ID"""
        if not self.langfuse_enabled:
            return None
        try:
            return langfuse_context.get_current_trace_id()
        except Exception as e:
            self.log_error("Failed to get trace ID", error=str(e))
            return None

    def update_current_observation(self, **kwargs):
        """Update the current observation with additional metadata"""
        if not self.langfuse_enabled:
            return
        try:
            langfuse_context.update_current_observation(**kwargs)
        except Exception as e:
            self.log_error("Failed to update observation", error=str(e))

    def update_current_trace(self, **kwargs):
        """Update the current trace with additional metadata"""
        if not self.langfuse_enabled:
            return
        try:
            langfuse_context.update_current_trace(**kwargs)
        except Exception as e:
            self.log_error("Failed to update trace", error=str(e))

    def score_current_observation(
        self, name: str, value: float, comment: Optional[str] = None
    ):
        """Score the current observation"""
        if not self.langfuse_enabled:
            return
        try:
            langfuse_context.score_current_observation(
                name=name, value=value, comment=comment
            )
        except Exception as e:
            self.log_error("Failed to score observation", error=str(e))

    def score_current_trace(
        self, name: str, value: float, comment: Optional[str] = None
    ):
        """Score the current trace"""
        if not self.langfuse_enabled:
            return
        try:
            langfuse_context.score_current_trace(
                name=name, value=value, comment=comment
            )
        except Exception as e:
            self.log_error("Failed to score trace", error=str(e))

    # Structured Logging Methods
    def log_info(self, message: str, **kwargs):
        """Log info message with context"""
        if not self.enable_structured_logging:
            return

        context = self.get_trace_context()
        # Add Langfuse trace context if available
        if self.langfuse_enabled:
            try:
                trace_id = langfuse_context.get_current_trace_id()
                if trace_id:
                    context["langfuse_trace_id"] = trace_id
            except:
                pass

        context.update(kwargs)
        self.logger.info(message, **context)

    def log_warning(self, message: str, **kwargs):
        """Log warning message with context"""
        if not self.enable_structured_logging:
            return

        context = self.get_trace_context()
        # Add Langfuse trace context if available
        if self.langfuse_enabled:
            try:
                trace_id = langfuse_context.get_current_trace_id()
                if trace_id:
                    context["langfuse_trace_id"] = trace_id
            except:
                pass

        context.update(kwargs)
        self.logger.warning(message, **context)

    def log_error(self, message: str, **kwargs):
        """Log error message with context"""
        if not self.enable_structured_logging:
            return

        context = self.get_trace_context()
        # Add Langfuse trace context if available
        if self.langfuse_enabled:
            try:
                trace_id = langfuse_context.get_current_trace_id()
                if trace_id:
                    context["langfuse_trace_id"] = trace_id
            except:
                pass

        context.update(kwargs)
        self.logger.error(message, **context)
        self.track_error("logged_error")

    def log_debug(self, message: str, **kwargs):
        """Log debug message with context"""
        if not self.enable_structured_logging:
            return

        context = self.get_trace_context()
        # Add Langfuse trace context if available
        if self.langfuse_enabled:
            try:
                trace_id = langfuse_context.get_current_trace_id()
                if trace_id:
                    context["langfuse_trace_id"] = trace_id
            except:
                pass

        context.update(kwargs)
        self.logger.debug(message, **context)

    # Decorator Methods
    def monitor_function(self, operation_name: Optional[str] = None):
        """Decorator to monitor function execution with Langfuse @observe integration"""

        def decorator(func):
            # Apply Langfuse @observe decorator first
            observed_func = observe()(func)

            @wraps(observed_func)
            async def async_wrapper(*args, **kwargs):
                op_name = operation_name or func.__name__
                start_time = time.time()

                try:
                    self.log_info(f"Starting {op_name}", operation=op_name)

                    # Update Langfuse observation with service context
                    if self.langfuse_enabled:
                        self.update_current_observation(
                            name=op_name,
                            metadata={
                                "service": self.service_name,
                                "operation": op_name,
                                "function": func.__name__,
                            },
                        )

                    result = await observed_func(*args, **kwargs)
                    duration = time.time() - start_time

                    self.track_request(op_name, "FUNC", "success", duration)
                    self.log_info(
                        f"Completed {op_name}", operation=op_name, duration=duration
                    )
                    return result

                except Exception as e:
                    duration = time.time() - start_time
                    self.track_request(op_name, "FUNC", "error", duration)
                    self.log_error(
                        f"Failed {op_name}",
                        operation=op_name,
                        error=str(e),
                        duration=duration,
                    )
                    raise

            @wraps(observed_func)
            def sync_wrapper(*args, **kwargs):
                op_name = operation_name or func.__name__
                start_time = time.time()

                try:
                    self.log_info(f"Starting {op_name}", operation=op_name)

                    # Update Langfuse observation with service context
                    if self.langfuse_enabled:
                        self.update_current_observation(
                            name=op_name,
                            metadata={
                                "service": self.service_name,
                                "operation": op_name,
                                "function": func.__name__,
                            },
                        )

                    result = observed_func(*args, **kwargs)
                    duration = time.time() - start_time

                    self.track_request(op_name, "FUNC", "success", duration)
                    self.log_info(
                        f"Completed {op_name}", operation=op_name, duration=duration
                    )
                    return result

                except Exception as e:
                    duration = time.time() - start_time
                    self.track_request(op_name, "FUNC", "error", duration)
                    self.log_error(
                        f"Failed {op_name}",
                        operation=op_name,
                        error=str(e),
                        duration=duration,
                    )
                    raise

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return decorator

    # Health Check Methods
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "service": self.service_name,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        # Check Redis connection
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health_status["checks"]["redis"] = "healthy"
            except Exception as e:
                health_status["checks"]["redis"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"

        # Check Langfuse connection
        if self.langfuse_enabled:
            try:
                # Use auth_check for verification
                langfuse_context.auth_check()
                health_status["checks"]["langfuse"] = "healthy"
            except Exception as e:
                health_status["checks"]["langfuse"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"

        return health_status

    def flush(self):
        """Flush all pending observations to Langfuse"""
        if self.langfuse_enabled:
            try:
                langfuse_context.flush()
            except Exception as e:
                self.log_error("Failed to flush Langfuse observations", error=str(e))


# Global monitoring instance
_global_monitor: Optional[PMOVESMonitoring] = None


def get_monitor(service_name: Optional[str] = None) -> PMOVESMonitoring:
    """Get or create global monitoring instance"""
    global _global_monitor

    if _global_monitor is None:
        _global_monitor = PMOVESMonitoring(
            service_name=service_name or "pmoves-service"
        )

    return _global_monitor


def init_monitoring(
    service_name: str,
    langfuse_public_key: Optional[str] = None,
    langfuse_secret_key: Optional[str] = None,
    langfuse_host: Optional[str] = None,
    redis_url: Optional[str] = None,
) -> PMOVESMonitoring:
    """Initialize global monitoring instance"""
    global _global_monitor

    _global_monitor = PMOVESMonitoring(
        service_name=service_name,
        langfuse_public_key=langfuse_public_key,
        langfuse_secret_key=langfuse_secret_key,
        langfuse_host=langfuse_host,
        redis_url=redis_url,
    )

    return _global_monitor


# Convenience decorators for common use cases
def observe_llm_call(name: Optional[str] = None, **kwargs):
    """Decorator for LLM calls with automatic metrics tracking"""

    def decorator(func):
        # Apply Langfuse observe decorator with generation type
        observed_func = observe(as_type="generation", name=name, **kwargs)(func)

        @wraps(observed_func)
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            start_time = time.time()

            try:
                result = observed_func(*args, **kwargs)
                duration = time.time() - start_time

                # Extract provider and model from function name or kwargs
                provider = kwargs.get("provider", "unknown")
                model = kwargs.get("model", "unknown")

                monitor.track_llm_call(provider, model, "success", duration)
                return result

            except Exception as e:
                duration = time.time() - start_time
                provider = kwargs.get("provider", "unknown")
                model = kwargs.get("model", "unknown")

                monitor.track_llm_call(provider, model, "error", duration)
                raise

        return wrapper

    return decorator


def observe_agent_operation(agent_type: str, operation: str):
    """Decorator for agent operations with automatic metrics tracking"""

    def decorator(func):
        observed_func = observe(name=f"{agent_type}_{operation}")(func)

        @wraps(observed_func)
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            start_time = time.time()

            try:
                result = observed_func(*args, **kwargs)
                duration = time.time() - start_time

                monitor.track_agent_operation(
                    agent_type, operation, "success", duration
                )
                return result

            except Exception as e:
                duration = time.time() - start_time
                monitor.track_agent_operation(agent_type, operation, "error", duration)
                raise

        return wrapper

    return decorator
