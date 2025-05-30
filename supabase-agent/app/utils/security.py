"""
Security Middleware for PMOVES Supabase Agent
Adapted from pmoves-pipecat-agent/security/middleware.py

This module provides security features, primarily focused on rate limiting
for the Supabase Agent. Other features can be enabled or disabled via config.
"""

import os
import re
import time
import json
import hashlib
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from pathlib import Path
import redis.asyncio as redis
from fastapi import Request, Response, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Commented out if auth_enabled is False by default
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import bleach # Optional: for advanced input sanitization
import validators # Optional: for URL validation in input sanitization

# Configure logging
# logging.basicConfig(level=logging.INFO) # Avoid reconfiguring root logger if already done in main app
logger = logging.getLogger(__name__)


class SecurityConfig(BaseModel):
    """Security configuration"""

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Requests per window")
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds" # Defaulted to 60s as per prompt example
    )
    # rate_limit_burst: int = Field(default=20, description="Burst requests allowed") # Not used in current RateLimiter logic

    # Redis configuration
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL")
    redis_prefix: str = Field(
        default="pmoves_supabase_agent:security:", description="Redis key prefix" # Agent-specific prefix
    )

    # Authentication (defaulted to False for supabase-agent, can be overridden by env vars)
    auth_enabled: bool = Field(default=False, description="Enable authentication")
    jwt_secret: str = Field(default="", description="JWT secret key") # Not used if auth_enabled is False
    api_keys: List[str] = Field(default=[], description="Valid API keys") # Not used if auth_enabled is False

    # Input validation (defaulted to basic for supabase-agent)
    max_request_size: int = Field(
        default=10 * 1024 * 1024, description="Max request size in bytes" # 10MB
    )
    max_json_depth: int = Field(default=10, description="Max JSON nesting depth") # Usually safe
    allowed_content_types: List[str] = Field(
        default=["application/json"], # Supabase agent primarily uses JSON
        description="Allowed content types",
    )
    input_validation_enabled: bool = Field(default=False, description="Enable advanced input validation (SQLi, XSS)")


    # File upload security (likely not applicable to supabase-agent, defaulted to off/restrictive)
    file_security_enabled: bool = Field(default=False, description="Enable file upload security features")
    max_file_size: int = Field(
        default=1 * 1024 * 1024, description="Max file size in bytes" # 1MB, if ever used
    )
    allowed_file_extensions: List[str] = Field(
        default=[], description="Allowed file extensions"
    )
    quarantine_dir: str = Field(
        default="/tmp/supabase_agent_quarantine", description="Quarantine directory"
    )

    # Security headers
    security_headers_enabled: bool = Field(
        default=True, description="Enable security headers"
    )
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins") # Adjust for production

    # Logging
    security_logging_enabled: bool = Field(
        default=True, description="Enable security logging for warnings/errors"
    )
    log_requests: bool = Field(default=True, description="Log all requests at INFO level")
    # log_responses: bool = Field(default=False, description="Log responses") # Generally too verbose


class RateLimiter:
    """Redis-based rate limiter with sliding window"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None

    async def initialize(self):
        """Initialize Redis connection"""
        if not self.config.rate_limit_enabled:
            logger.info("Rate limiting is disabled. Skipping Redis connection.")
            return False
        try:
            self.redis_client = redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            logger.info(f"Rate limiter Redis connection established for prefix '{self.config.redis_prefix}'")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis for rate limiter: {e}", exc_info=True)
            # Disable rate limiting if Redis connection fails
            self.config.rate_limit_enabled = False
            return False

    async def is_allowed(
        self, identifier: str, endpoint: str = "default"
    ) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed under rate limit"""
        if not self.config.rate_limit_enabled or not self.redis_client:
            return True, {} # Fail open if disabled or Redis not available

        try:
            key = f"{self.config.redis_prefix}rate_limit:{identifier}:{endpoint}"
            current_time = int(time.time())
            window_start = current_time - self.config.rate_limit_window

            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, self.config.rate_limit_window)
            results = await pipe.execute()
            
            # results[0] is from zremrangebyscore, results[1] from zcard, results[2] from zadd, results[3] from expire
            current_count = results[1] 

            allowed = current_count < self.config.rate_limit_requests

            reset_time = current_time + self.config.rate_limit_window # Simplified reset time

            return allowed, {
                "current_count": current_count + 1, # Return the count including current request
                "limit": self.config.rate_limit_requests,
                "window": self.config.rate_limit_window,
                "reset_time": reset_time,
                "remaining": max(0, self.config.rate_limit_requests - (current_count + 1)),
            }

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}", exc_info=True)
            return True, {} # Fail open


class InputValidator:
    """Input validation and sanitization"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|TRUNCATE)\b)",
            r"(--|#|/\*|\*/|;)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        ]
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>", r"javascript:", r"vbscript:",
            r"on\w+\s*=", r"<iframe[^>]*>.*?</iframe>", r"data:[^,]*,"
        ]
        self.path_traversal_patterns = [
            r"\.\./", r"\.\.\\", r"%2e%2e%2f", r"%2e%2e%5c",
        ]

    def validate_json_depth(self, data: Any, current_depth: int = 0) -> bool:
        if not self.config.input_validation_enabled: return True
        if current_depth > self.config.max_json_depth: return False
        if isinstance(data, dict):
            return all(self.validate_json_depth(v, current_depth + 1) for v in data.values())
        if isinstance(data, list):
            return all(self.validate_json_depth(i, current_depth + 1) for i in data)
        return True

    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        if not self.config.input_validation_enabled: return False
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns)

    def detect_sql_injection(self, text: str) -> bool:
        return self._check_patterns(text, self.sql_patterns)

    def detect_xss(self, text: str) -> bool:
        # More comprehensive XSS detection might involve bleach or other libraries
        # For now, basic pattern matching if input_validation_enabled
        return self._check_patterns(text, self.xss_patterns)

    def detect_path_traversal(self, text: str) -> bool:
        return self._check_patterns(text, self.path_traversal_patterns)

    def sanitize_text(self, text: str) -> str:
        if not self.config.input_validation_enabled: return text
        # Using bleach for sanitization if advanced validation is on.
        # Customize tags/attributes if HTML content is ever expected. For Supabase agent, likely not.
        return bleach.clean(text, tags=[], attributes={}, strip=True)

    def validate_url(self, url: str) -> bool:
        if not self.config.input_validation_enabled: return True
        if not validators.url(url): return False
        dangerous_protocols = ["javascript:", "data:", "vbscript:", "file:"]
        return not any(url.lower().startswith(p) for p in dangerous_protocols)

    def validate_file_upload(self, filename: str, content: bytes) -> tuple[bool, str]:
        if not self.config.file_security_enabled: return True, "File security disabled"
        
        if len(content) > self.config.max_file_size:
            return False, f"File size exceeds limit."
        
        file_path = Path(filename)
        if self.config.allowed_file_extensions and \
           file_path.suffix.lower() not in self.config.allowed_file_extensions:
            return False, f"File extension not allowed."
        
        if b"\x00" in content: return False, "File contains null bytes."
        
        # Basic magic number validation (can be expanded)
        # For supabase-agent, file uploads are not typical, so this is minimal.
        return True, "File validation passed (basic)"


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config: SecurityConfig):
        super().__init__(app)
        self.config = config
        self.rate_limiter = RateLimiter(config)
        self.input_validator = InputValidator(config)
        # self.security_bearer = HTTPBearer(auto_error=False) # Only if auth_enabled

        if self.config.file_security_enabled:
            Path(config.quarantine_dir).mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize middleware components, particularly the rate limiter's Redis connection."""
        await self.rate_limiter.initialize()

    def get_client_identifier(self, request: Request) -> str:
        # Simplified for Supabase Agent: primarily IP-based if auth is off.
        if self.config.auth_enabled:
            auth_header = request.headers.get("x-api-key") # Example: use API key if auth is on
            if auth_header:
                return hashlib.md5(auth_header.encode()).hexdigest()

        client_ip = request.client.host if request.client else "unknown_client"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        return client_ip

    def add_security_headers(self, response: Response):
        if not self.config.security_headers_enabled: return
        headers = {
            "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            # "Content-Security-Policy": "default-src 'self'", # Can be too restrictive; customize if needed
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        for header, value in headers.items(): response.headers[header] = value
        if self.config.cors_origins: # Basic CORS, real CORS middleware might be better for complex needs
             response.headers["Access-Control-Allow-Origin"] = ",".join(self.config.cors_origins)


    async def validate_authentication(self, request: Request) -> Dict[str, Any]:
        # Simplified for Supabase Agent - default to not requiring auth unless configured
        if not self.config.auth_enabled:
            return {"authenticated": False, "user": "anonymous", "method": "none"}

        api_key = request.headers.get("x-api-key")
        if api_key and api_key in self.config.api_keys:
            return {"authenticated": True, "user": f"api_key_{api_key[:8]}", "method": "api_key"}
        
        # Allow public paths even if auth is generally enabled
        public_paths = ["/health", "/docs", "/openapi.json", "/"] # Add root path as public
        if request.url.path in public_paths:
            return {"authenticated": False, "user": "public_access", "method": "none"}

        # If auth is enabled and no valid API key for a non-public path
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )


    async def validate_request_content(self, request: Request) -> Optional[str]:
        content_type = request.headers.get("content-type", "").split(";")[0]
        if content_type and content_type not in self.config.allowed_content_types:
            return f"Content type {content_type} not allowed. Allowed: {self.config.allowed_content_types}"

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.config.max_request_size:
                    return f"Request size exceeds limit of {self.config.max_request_size} bytes"
            except ValueError:
                 return "Invalid Content-Length header."
        return None

    async def log_security_event(self, event_type: str, request: Request, details: Dict[str, Any]):
        if not self.config.security_logging_enabled: return
        log_data = {
            "timestamp": datetime.utcnow().isoformat(), "event_type": event_type,
            "client_ip": request.client.host if request.client else "N/A",
            "path": request.url.path, "method": request.method, "details": details,
        }
        logger.warning(f"Security Event: {json.dumps(log_data)}")


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_id = "unknown" # Default client_id

        try:
            client_id = self.get_client_identifier(request)

            # 1. Rate limiting
            if self.config.rate_limit_enabled:
                endpoint = f"{request.method}:{request.url.path}"
                allowed, rate_info = await self.rate_limiter.is_allowed(client_id, endpoint)
                if not allowed:
                    await self.log_security_event("rate_limit_exceeded", request, {"client_id": client_id, "rate_info": rate_info})
                    response = JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                            content={"error": "Rate limit exceeded", "rate_info": rate_info})
                    self.add_security_headers(response)
                    return response
            
            # 2. Authentication (if enabled)
            try:
                auth_result = await self.validate_authentication(request)
            except HTTPException as auth_exc:
                 await self.log_security_event("authentication_failed", request, {"client_id": client_id, "error": auth_exc.detail})
                 response = JSONResponse(status_code=auth_exc.status_code, content={"error": auth_exc.detail})
                 self.add_security_headers(response)
                 return response


            # 3. Request content validation (basic)
            content_error = await self.validate_request_content(request)
            if content_error:
                await self.log_security_event("invalid_request_content", request, {"error": content_error, "client_id": client_id})
                response = JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": content_error})
                self.add_security_headers(response)
                return response
            
            # Advanced Input Validation (SQLi, XSS) if enabled
            if self.config.input_validation_enabled:
                # This part would need to inspect request body/params, which is complex in middleware
                # For now, this is a placeholder. Actual validation of body needs more.
                # Example: if request.method in ["POST", "PUT"]:
                #   try:
                #       body = await request.json() # This consumes the body! Careful.
                #       # Perform validation on body fields...
                #   except: pass # Handle cases where body isn't JSON or already consumed
                pass


            request.state.security = {"client_id": client_id, "auth": auth_result if 'auth_result' in locals() else None}
            response = await call_next(request)
            self.add_security_headers(response)

            if self.config.log_requests:
                processing_time = time.time() - start_time
                logger.info(
                    f"Request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {processing_time:.3f}s - Client: {client_id}"
                )
            return response

        except Exception as e:
            logger.error(f"Unhandled exception in security middleware: {e}", exc_info=True)
            await self.log_security_event("middleware_error", request, {"error": str(e), "client_id": client_id})
            response = JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    content={"error": "Internal server error during security processing"})
            self.add_security_headers(response)
            return response

# SecurityUtils can remain if other parts of supabase-agent might use them,
# but are not core to this rate-limiting focused middleware adaptation.
class SecurityUtils:
    @staticmethod
    def generate_api_key() -> str:
        import secrets
        return secrets.token_urlsafe(32)

    # Other utils like hash_password, verify_password, create_jwt_token, verify_jwt_token
    # can be kept if there's any potential use, or removed if strictly not needed.
    # For supabase-agent, if auth_enabled is False, these are not directly used by the middleware.
