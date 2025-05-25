"""
PMOVES Security Module

This module provides comprehensive security features for the PMOVES Pipecat agents:
- Rate limiting with Redis backend
- Input validation and sanitization
- Authentication and authorization
- Security headers and middleware
- Security utilities
"""

from .middleware import (
    SecurityConfig,
    SecurityMiddleware,
    RateLimiter,
    InputValidator,
    SecurityUtils,
    create_security_middleware,
)

__all__ = [
    "SecurityConfig",
    "SecurityMiddleware",
    "RateLimiter",
    "InputValidator",
    "SecurityUtils",
    "create_security_middleware",
]

__version__ = "1.0.0"
