import os
import logging
from fastapi import Request, HTTPException, status, Response
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import json
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

API_KEY_NAME = os.getenv("API_KEY_NAME", "X-API-KEY")
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

VALID_API_KEYS_STR = os.getenv("VALID_API_KEYS")
VALID_API_KEYS = VALID_API_KEYS_STR.split(",") if VALID_API_KEYS_STR else []

if not VALID_API_KEYS:
    logger.warning(
        "No VALID_API_KEYS set in environment. API key authentication will deny all requests that require it."
    )
elif "" in VALID_API_KEYS:
    logger.warning(
        "VALID_API_KEYS is set to an empty string. This is not a secure configuration. API key authentication will deny all requests."
    )
    VALID_API_KEYS = []
else:
    logger.info(
        f"API Key Authentication enabled. {len(VALID_API_KEYS)} valid key(s) loaded."
    )

# Define paths that should be exempt from API key authentication
# Ensure these paths are well-defined and do not unintentionally expose sensitive endpoints.
EXEMPT_PATHS = [
    "/transcription-status",
    "/docs",
    "/openapi.json",
    "/health",
    "/healthz",
    "/metrics",
    "/monitoring/status",
    "/combined-updates",
    "/api/download-status",
    "/api/default-directory",
    "/api/app-config",
    "/api/list-workspace",
    "/test-event-loop-policy",
    "/",
    "/process-video/",
]

# Define path prefixes that should be exempt
EXEMPT_PREFIXES = [
    "/static",
    "/view-pdf",
    "/download-pdf",
]

# Get the API key from environment variables
SERVER_API_KEY = os.getenv(
    "BACKEND_API_KEY"
)  # Used by backend to protect its own endpoints
# ALLOWED_KEYS is a comma-separated string of keys that clients can use
ALLOWED_API_KEYS_STR = os.getenv("ALLOWED_API_KEYS", "")
ALLOWED_API_KEYS = set(
    key.strip() for key in ALLOWED_API_KEYS_STR.split(",") if key.strip()
)

# Add the server\'s own API key to the set of allowed keys if it\'s defined
if SERVER_API_KEY:
    ALLOWED_API_KEYS.add(SERVER_API_KEY)

if not ALLOWED_API_KEYS:
    logger.warning(
        "No API keys configured in ALLOWED_API_KEYS or BACKEND_API_KEY. API key security will be ineffective."
    )


DISABLE_API_KEY_MIDDLEWARE = os.getenv("DISABLE_API_KEY_MIDDLEWARE", "false").lower() == "true"


class APIKeySecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if DISABLE_API_KEY_MIDDLEWARE:
            logger.warning(
                "DEVELOPMENT MODE: APIKeySecurityMiddleware is currently DISABLED. All requests are being allowed without API key authentication."
            )
            response = await call_next(request)
            return response

        # Check if the current request path is in EXEMPT_PATHS or starts with an EXEMPT_PREFIX
        if request.url.path in EXEMPT_PATHS or any(
            request.url.path.startswith(prefix) for prefix in EXEMPT_PREFIXES
        ):
            logger.debug(f"Path {request.url.path} is exempt from API key auth.")
            return await call_next(request)

        # Handle OPTIONS requests for CORS preflight
        if request.method == "OPTIONS":
            logger.debug(
                f"Handling OPTIONS request for {request.url.path}, bypassing API key check."
            )
            # These headers should ideally be managed by the global CORS middleware,
            # but returning them here ensures preflight requests pass if they hit this middleware first.
            # The main FastAPI CORS middleware should handle the actual GET/POST etc. requests.
            # However, the 401 indicates this middleware *is* intercepting and denying OPTIONS.
            return Response(
                status_code=status.HTTP_200_OK,
                headers={
                    "Access-Control-Allow-Origin": request.headers.get(
                        "Origin", "*"
                    ),  # Be more specific if possible
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",  # Mirror main.py
                    "Access-Control-Allow-Headers": request.headers.get(
                        "Access-Control-Request-Headers", "*"
                    ),  # Reflect requested headers
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "86400",  # Cache preflight for 1 day
                },
            )

        logger.debug(f"Attempting API key auth for path: {request.url.path}")

        api_key_received = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                api_key_received = parts[1]
                logger.debug(
                    f"Extracted API key from Authorization Bearer header for {request.url.path}"
                )

        if not api_key_received:
            # Fallback to custom header if Bearer token not found or invalid format
            custom_api_key = await API_KEY_HEADER(request)
            if custom_api_key:
                api_key_received = custom_api_key
                logger.debug(
                    f"Extracted API key from {API_KEY_NAME} header for {request.url.path}"
                )

        if not api_key_received:
            logger.warning(
                f"API key missing from both Authorization and {API_KEY_NAME} headers for {request.url.path}. Denying access."
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "API key required. Provide via 'Authorization: Bearer <key>' or 'X-API-KEY: <key>' header."
                },
            )

        if api_key_received not in ALLOWED_API_KEYS:
            logger.warning(
                f"Invalid API key provided for {request.url.path}. Key: '{api_key_received[:5]}...'. Denying access."
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid API Key"},
            )

        logger.debug(f"API key validated successfully for {request.url.path}.")
        # If API key is valid, proceed with the request
        response = await call_next(request)
        return response
