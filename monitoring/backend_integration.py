"""
PMOVES Backend Monitoring Integration

This module provides seamless integration between the PMOVES monitoring system
and the existing 4,684-line FastAPI backend with Supabase integration.

Features:
- FastAPI middleware integration
- Supabase operation monitoring
- Agent endpoint tracking
- LLM call monitoring for existing providers
- Search operation tracking
- Content processing monitoring
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from monitoring.pmoves_monitoring import (
    init_monitoring,
    PMOVESMonitoring,
    observe_llm_call,
    observe_agent_operation,
    get_monitor,
)
from langfuse.decorators import observe, langfuse_context


class PMOVESBackendMonitoring(BaseHTTPMiddleware):
    """FastAPI middleware for automatic request monitoring"""

    def __init__(self, app: FastAPI, monitor: PMOVESMonitoring):
        super().__init__(app)
        self.monitor = monitor

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate correlation ID for this request
        correlation_id = self.monitor.generate_correlation_id()

        # Set trace context
        self.monitor.set_trace_context(correlation_id)

        # Track request start
        start_time = time.time()
        endpoint = request.url.path
        method = request.method

        # Log request start
        self.monitor.log_info(
            "Request started",
            endpoint=endpoint,
            method=method,
            correlation_id=correlation_id,
            user_agent=request.headers.get("user-agent", "unknown"),
        )

        try:
            # Process request
            response = await call_next(request)
            duration = time.time() - start_time

            # Determine status
            status = "success" if response.status_code < 400 else "error"

            # Track metrics
            self.monitor.track_request(endpoint, method, status, duration)

            # Log completion
            self.monitor.log_info(
                "Request completed",
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                duration=duration,
                correlation_id=correlation_id,
            )

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Track error
            self.monitor.track_request(endpoint, method, "error", duration)
            self.monitor.track_error("request_error", "error")

            # Log error
            self.monitor.log_error(
                "Request failed",
                endpoint=endpoint,
                method=method,
                error=str(e),
                duration=duration,
                correlation_id=correlation_id,
            )

            raise


def setup_backend_monitoring(
    app: FastAPI, service_name: str = "pmoves-backend"
) -> PMOVESMonitoring:
    """
    Set up comprehensive monitoring for the PMOVES FastAPI backend

    Args:
        app: FastAPI application instance
        service_name: Name of the service for monitoring

    Returns:
        PMOVESMonitoring instance
    """

    # Initialize monitoring
    monitor = init_monitoring(service_name=service_name)

    # Add middleware for automatic request tracking
    app.add_middleware(PMOVESBackendMonitoring, monitor=monitor)

    # Add metrics endpoint
    @app.get("/metrics")
    async def get_metrics():
        """Prometheus metrics endpoint"""
        return Response(content=monitor.get_metrics(), media_type="text/plain")

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint with monitoring integration"""
        health_status = await monitor.health_check()
        return health_status

    # Add monitoring status endpoint
    @app.get("/monitoring/status")
    async def monitoring_status():
        """Get current monitoring status and configuration"""
        return {
            "service": service_name,
            "monitoring_enabled": True,
            "langfuse_enabled": monitor.langfuse_enabled,
            "prometheus_enabled": monitor.enable_prometheus,
            "structured_logging": monitor.enable_structured_logging,
            "current_trace_url": monitor.get_current_trace_url(),
        }

    return monitor


# Decorators for existing backend functions
def monitor_supabase_operation(operation_type: str):
    """Decorator for Supabase database operations"""

    def decorator(func):
        @observe_agent_operation("supabase", operation_type)
        async def wrapper(*args, **kwargs):
            monitor = get_monitor()

            # Update observation with Supabase context
            monitor.update_current_observation(
                name=f"Supabase {operation_type}",
                metadata={
                    "database": "supabase",
                    "operation": operation_type,
                    "function": func.__name__,
                },
            )

            try:
                result = await func(*args, **kwargs)

                # Track successful operation
                monitor.track_agent_operation("supabase", operation_type, "success")

                return result

            except Exception as e:
                # Track failed operation
                monitor.track_agent_operation("supabase", operation_type, "error")
                monitor.log_error(f"Supabase {operation_type} failed", error=str(e))
                raise

        return wrapper

    return decorator


def monitor_search_operation(search_type: str):
    """Decorator for search operations (psearchworking.py integration)"""

    def decorator(func):
        @observe(name=f"Search: {search_type}")
        async def wrapper(*args, **kwargs):
            monitor = get_monitor()
            start_time = time.time()

            # Update trace with search context
            monitor.update_current_trace(
                name=f"PMOVES Search: {search_type}",
                metadata={
                    "search_type": search_type,
                    "search_engine": "psearchworking",
                    "function": func.__name__,
                },
            )

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Track search metrics
                monitor.track_search(search_type, "success", duration)

                # Update observation with results
                if hasattr(result, "__len__"):
                    monitor.update_current_observation(
                        metadata={"results_count": len(result), "duration": duration}
                    )

                monitor.log_info(
                    f"Search {search_type} completed",
                    duration=duration,
                    results_count=len(result)
                    if hasattr(result, "__len__")
                    else "unknown",
                )

                return result

            except Exception as e:
                duration = time.time() - start_time
                monitor.track_search(search_type, "error", duration)
                monitor.log_error(
                    f"Search {search_type} failed", error=str(e), duration=duration
                )
                raise

        return wrapper

    return decorator


def monitor_content_processing(content_type: str, operation: str):
    """Decorator for content processing operations (pmoves_upserter.py integration)"""

    def decorator(func):
        @observe(name=f"Content: {operation}")
        async def wrapper(*args, **kwargs):
            monitor = get_monitor()

            # Update trace with content processing context
            monitor.update_current_trace(
                name=f"Content Processing: {operation}",
                metadata={
                    "content_type": content_type,
                    "operation": operation,
                    "processor": "pmoves_upserter",
                },
            )

            try:
                result = await func(*args, **kwargs)

                # Track content processing
                monitor.track_content_processing(content_type, operation, "success")

                monitor.log_info(
                    f"Content {operation} completed",
                    content_type=content_type,
                    operation=operation,
                )

                return result

            except Exception as e:
                monitor.track_content_processing(content_type, operation, "error")
                monitor.log_error(
                    f"Content {operation} failed",
                    content_type=content_type,
                    error=str(e),
                )
                raise

        return wrapper

    return decorator


def monitor_llm_provider_call(provider: str, model: str):
    """Decorator for LLM provider calls (OpenAI, Groq, Anthropic)"""

    def decorator(func):
        @observe_llm_call(name=f"{provider} {model}")
        async def wrapper(*args, **kwargs):
            monitor = get_monitor()
            start_time = time.time()

            # Update observation with LLM context
            monitor.update_current_observation(
                model=f"{provider}/{model}",
                metadata={
                    "provider": provider,
                    "model": model,
                    "function": func.__name__,
                },
            )

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Extract token usage if available
                input_tokens = 0
                output_tokens = 0
                cost = 0.0

                if hasattr(result, "usage"):
                    if hasattr(result.usage, "prompt_tokens"):
                        input_tokens = result.usage.prompt_tokens
                    if hasattr(result.usage, "completion_tokens"):
                        output_tokens = result.usage.completion_tokens

                # Track LLM metrics
                monitor.track_llm_call(
                    provider=provider,
                    model=model,
                    status="success",
                    duration=duration,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                )

                # Update observation with usage
                monitor.update_current_observation(
                    usage_details={
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens,
                        "duration": duration,
                    }
                )

                return result

            except Exception as e:
                duration = time.time() - start_time
                monitor.track_llm_call(provider, model, "error", duration)
                monitor.log_error(
                    f"LLM call to {provider}/{model} failed", error=str(e)
                )
                raise

        return wrapper

    return decorator


# Integration helpers for existing backend code
class BackendIntegrationHelpers:
    """Helper methods for integrating monitoring into existing backend code"""

    @staticmethod
    def wrap_video_processing():
        """Wrap video processing functions with monitoring"""
        return monitor_content_processing("video", "processing")

    @staticmethod
    def wrap_transcription():
        """Wrap transcription functions with monitoring"""
        return monitor_content_processing("audio", "transcription")

    @staticmethod
    def wrap_vector_search():
        """Wrap vector search functions with monitoring"""
        return monitor_search_operation("vector")

    @staticmethod
    def wrap_keyword_search():
        """Wrap keyword search functions with monitoring"""
        return monitor_search_operation("keyword")

    @staticmethod
    def wrap_hybrid_search():
        """Wrap hybrid search functions with monitoring"""
        return monitor_search_operation("hybrid")

    @staticmethod
    def wrap_content_fetch():
        """Wrap content fetching functions with monitoring"""
        return monitor_content_processing("web", "fetch")

    @staticmethod
    def wrap_supabase_insert():
        """Wrap Supabase insert operations with monitoring"""
        return monitor_supabase_operation("insert")

    @staticmethod
    def wrap_supabase_select():
        """Wrap Supabase select operations with monitoring"""
        return monitor_supabase_operation("select")

    @staticmethod
    def wrap_supabase_update():
        """Wrap Supabase update operations with monitoring"""
        return monitor_supabase_operation("update")

    @staticmethod
    def wrap_openai_call():
        """Wrap OpenAI API calls with monitoring"""
        return monitor_llm_provider_call("openai", "gpt-4")

    @staticmethod
    def wrap_groq_call():
        """Wrap Groq API calls with monitoring"""
        return monitor_llm_provider_call("groq", "llama")

    @staticmethod
    def wrap_anthropic_call():
        """Wrap Anthropic API calls with monitoring"""
        return monitor_llm_provider_call("anthropic", "claude")


# Example integration for main.py
def integrate_with_main_app(app: FastAPI):
    """
    Example integration with the main FastAPI app

    Add this to your backend/app/main.py:

    from monitoring.backend_integration import setup_backend_monitoring

    # After creating your FastAPI app
    monitor = setup_backend_monitoring(app, "pmoves-backend")
    """

    # Set up monitoring
    monitor = setup_backend_monitoring(app, "pmoves-backend")

    # Example of wrapping existing endpoints
    helpers = BackendIntegrationHelpers()

    return monitor, helpers


# Configuration for Supabase integration
SUPABASE_MONITORING_CONFIG = {
    "track_queries": True,
    "track_inserts": True,
    "track_updates": True,
    "track_deletes": True,
    "track_rpc_calls": True,
    "track_realtime": True,
    "log_query_performance": True,
    "alert_on_slow_queries": True,
    "slow_query_threshold": 1.0,  # seconds
}

# Configuration for agent monitoring
AGENT_MONITORING_CONFIG = {
    "supabase_agent": {
        "track_search_operations": True,
        "track_upsert_operations": True,
        "track_table_management": True,
    },
    "transcribe_agent": {
        "track_audio_processing": True,
        "track_video_processing": True,
        "track_provider_calls": True,
    },
    "multimodal_agent": {
        "track_vision_analysis": True,
        "track_image_generation": True,
        "track_audio_processing": True,
    },
}
