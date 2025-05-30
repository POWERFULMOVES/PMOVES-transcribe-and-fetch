"""
SupabaseAgent - Specialized agent for Supabase database operations

This agent provides:
- Database query and manipulation
- Vector search capabilities
- Content upserting
- Real-time subscriptions
- Secure database operations
- Production-ready security features
"""

import os
import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import asyncpg
from pydantic import BaseModel, Field
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseConfig(BaseModel):
    """Configuration for Supabase agent"""

    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase service role key")
    max_connections: int = Field(default=10, description="Max database connections")
    timeout: int = Field(default=30, description="Query timeout in seconds")
    enable_rls: bool = Field(default=True, description="Enable Row Level Security")
    rate_limit_requests: int = Field(default=100, description="Requests per minute")
    max_query_size: int = Field(
        default=10000, description="Max query size in characters"
    )
    embedding_model: str = Field(default="text-embedding-ada-002", description="Default model for text embeddings.")


class DatabaseQuery(BaseModel):
    """Database query request model"""

    table: str = Field(..., description="Table name")
    operation: str = Field(..., description="Operation: select, insert, update, delete")
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Data for insert/update"
    )
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Query filters")
    columns: Optional[List[str]] = Field(default=None, description="Columns to select")
    limit: Optional[int] = Field(default=100, description="Result limit")


class VectorSearchQuery(BaseModel):
    """Vector search query model"""

    query_text: str = Field(..., description="Search query text")
    table: str = Field(default="document_embeddings", description="Table to search")
    similarity_threshold: float = Field(default=0.7, description="Similarity threshold")
    limit: int = Field(default=10, description="Number of results")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional filters"
    )


class SupabaseAgent:
    """Supabase database agent with comprehensive functionality and security"""

    def __init__(self, config: SupabaseConfig):
        self.config = config
        self.client: Optional[Client] = None
        self.connection_pool: Optional[asyncpg.Pool] = None
        self.status = "initializing"

        # Allowed tables for security
        self.allowed_tables = {
            "video_transcriptions",
            "video_transcriptions_full",
            "webpage_content",
            "document_embeddings",
            "media_content",
            "fetch_history",
            "messages",
        }

        # Read-only operations
        self.read_only_operations = {"select", "search"}

        # Rate limiting
        self.request_counts = {}
        self.last_cleanup = time.time()

    async def initialize(self) -> bool:
        """Initialize Supabase client and connection pool"""
        try:
            # Initialize Supabase client
            self.client = create_client(
                self.config.supabase_url,
                self.config.supabase_key,
                options=ClientOptions(
                    postgrest_client_timeout=self.config.timeout,
                    storage_client_timeout=self.config.timeout,
                ),
            )

            # Initialize connection pool for direct PostgreSQL access
            database_url = self._get_database_url()
            if database_url:
                self.connection_pool = await asyncpg.create_pool(
                    database_url,
                    min_size=1,
                    max_size=self.config.max_connections,
                    command_timeout=self.config.timeout,
                    server_settings={
                        "application_name": "pmoves_supabase_agent",
                        "search_path": "public",
                    },
                )

            self.status = "ready"
            logger.info("SupabaseAgent initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize SupabaseAgent: {e}")
            self.status = "error"
            return False

    def _get_database_url(self) -> Optional[str]:
        """Extract database URL from Supabase URL"""
        try:
            # Extract project ID from Supabase URL
            project_id = self.config.supabase_url.split("//")[1].split(".")[0]

            # Construct direct PostgreSQL URL
            # Note: This requires the database password to be available
            db_password = os.getenv("SUPABASE_DB_PASSWORD")
            if not db_password:
                logger.warning(
                    "SUPABASE_DB_PASSWORD not set, direct DB access unavailable"
                )
                return None

            return f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"

        except Exception as e:
            logger.error(f"Failed to construct database URL: {e}")
            return None

    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()

        # Cleanup old entries every 5 minutes
        if current_time - self.last_cleanup > 300:
            self._cleanup_rate_limit_data()
            self.last_cleanup = current_time

        # Get current minute window
        minute_window = int(current_time // 60)

        if client_id not in self.request_counts:
            self.request_counts[client_id] = {}

        # Count requests in current minute
        current_requests = self.request_counts[client_id].get(minute_window, 0)

        if current_requests >= self.config.rate_limit_requests:
            return False

        # Increment counter
        self.request_counts[client_id][minute_window] = current_requests + 1
        return True

    def _cleanup_rate_limit_data(self):
        """Remove old rate limit data"""
        current_time = time.time()
        current_minute = int(current_time // 60)

        for client_id in list(self.request_counts.keys()):
            # Remove entries older than 2 minutes
            self.request_counts[client_id] = {
                minute: count
                for minute, count in self.request_counts[client_id].items()
                if minute >= current_minute - 2
            }

            # Remove empty client entries
            if not self.request_counts[client_id]:
                del self.request_counts[client_id]

    async def execute_query(
        self, query: DatabaseQuery, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute a database query with security checks"""
        try:
            # Rate limiting check
            client_id = (
                user_context.get("client_id", "anonymous")
                if user_context
                else "anonymous"
            )
            if not self._check_rate_limit(client_id):
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please try again later.",
                    "data": None,
                }

            # Security validation
            if not self._validate_query(query, user_context):
                return {
                    "success": False,
                    "error": "Query validation failed",
                    "data": None,
                }

            # Route to appropriate handler
            if query.operation == "select":
                return await self._handle_select(query)
            elif query.operation == "insert":
                return await self._handle_insert(query)
            elif query.operation == "update":
                return await self._handle_update(query)
            elif query.operation == "delete":
                return await self._handle_delete(query)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported operation: {query.operation}",
                    "data": None,
                }

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {"success": False, "error": "Internal server error", "data": None}

    def _validate_query(
        self, query: DatabaseQuery, user_context: Optional[Dict] = None
    ) -> bool:
        """Validate query for security and permissions"""
        # Check table allowlist
        if query.table not in self.allowed_tables:
            logger.warning(f"Access denied to table: {query.table}")
            return False

        # Check operation permissions
        if user_context and user_context.get("role") == "read_only":
            if query.operation not in self.read_only_operations:
                logger.warning(f"Read-only user attempted {query.operation}")
                return False

        # Validate data for SQL injection patterns
        if query.data:
            if self._contains_sql_injection(query.data):
                logger.warning("Potential SQL injection detected")
                return False

        # Check query size limits
        query_str = json.dumps(query.dict())
        if len(query_str) > self.config.max_query_size:
            logger.warning(
                f"Query size {len(query_str)} exceeds limit {self.config.max_query_size}"
            )
            return False

        return True

    def _contains_sql_injection(self, data: Dict[str, Any]) -> bool:
        """Enhanced SQL injection detection"""
        dangerous_patterns = [
            r"(?i)(DROP\s+TABLE)",
            r"(?i)(DELETE\s+FROM)",
            r"(?i)(UPDATE\s+.*\s+SET)",
            r"(?i)(INSERT\s+INTO)",
            r"(?i)(UNION\s+SELECT)",
            r"(?i)(OR\s+1\s*=\s*1)",
            r"(?i)(AND\s+1\s*=\s*1)",
            r"(?i)(';\s*--)",
            r"(?i)(/\*.*\*/)",
            r"(?i)(EXEC\s*\()",
            r"(?i)(EXECUTE\s*\()",
            r"(?i)(xp_cmdshell)",
            r"(?i)(sp_executesql)",
        ]

        data_str = json.dumps(data)
        return any(re.search(pattern, data_str) for pattern in dangerous_patterns)

    async def _handle_select(self, query: DatabaseQuery) -> Dict[str, Any]:
        """Handle SELECT operations with enhanced security"""
        try:
            # Build query
            supabase_query = self.client.table(query.table).select(
                ",".join(query.columns) if query.columns else "*"
            )

            # Apply filters with validation
            if query.filters:
                for key, value in query.filters.items():
                    # Validate column names
                    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                        raise ValueError(f"Invalid column name: {key}")

                    if isinstance(value, dict) and "operator" in value:
                        # Handle complex filters like {"operator": "gte", "value": 100}
                        op = value["operator"]
                        val = value["value"]

                        # Validate operator
                        allowed_ops = [
                            "eq",
                            "neq",
                            "gt",
                            "gte",
                            "lt",
                            "lte",
                            "like",
                            "ilike",
                            "in",
                        ]
                        if op not in allowed_ops:
                            raise ValueError(f"Invalid operator: {op}")

                        supabase_query = getattr(supabase_query, op)(key, val)
                    else:
                        # Simple equality filter
                        supabase_query = supabase_query.eq(key, value)

            # Apply limit with maximum cap
            limit = min(query.limit or 100, 1000)  # Cap at 1000 records
            supabase_query = supabase_query.limit(limit)

            # Execute query
            response = supabase_query.execute()

            return {
                "success": True,
                "error": None,
                "data": response.data,
                "count": len(response.data),
            }

        except Exception as e:
            logger.error(f"Select query failed: {e}")
            return {"success": False, "error": str(e), "data": None}

    async def _handle_insert(self, query: DatabaseQuery) -> Dict[str, Any]:
        """Handle INSERT operations with validation"""
        try:
            if not query.data:
                return {
                    "success": False,
                    "error": "No data provided for insert",
                    "data": None,
                }

            # Validate data structure
            if not isinstance(query.data, dict):
                return {
                    "success": False,
                    "error": "Insert data must be a dictionary",
                    "data": None,
                }

            # Add timestamp if not present
            if "created_at" not in query.data:
                query.data["created_at"] = datetime.utcnow().isoformat()

            # Validate column names
            for key in query.data.keys():
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    return {
                        "success": False,
                        "error": f"Invalid column name: {key}",
                        "data": None,
                    }

            response = self.client.table(query.table).insert(query.data).execute()

            return {
                "success": True,
                "error": None,
                "data": response.data,
                "count": len(response.data),
            }

        except Exception as e:
            logger.error(f"Insert query failed: {e}")
            return {"success": False, "error": str(e), "data": None}

    async def _handle_update(self, query: DatabaseQuery) -> Dict[str, Any]:
        """Handle UPDATE operations with enhanced security"""
        try:
            if not query.data:
                return {
                    "success": False,
                    "error": "No data provided for update",
                    "data": None,
                }

            if not query.filters:
                return {
                    "success": False,
                    "error": "No filters provided for update (safety check)",
                    "data": None,
                }

            # Validate data structure
            if not isinstance(query.data, dict):
                return {
                    "success": False,
                    "error": "Update data must be a dictionary",
                    "data": None,
                }

            # Add timestamp
            query.data["updated_at"] = datetime.utcnow().isoformat()

            # Validate column names
            for key in query.data.keys():
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    return {
                        "success": False,
                        "error": f"Invalid column name: {key}",
                        "data": None,
                    }

            # Build update query
            supabase_query = self.client.table(query.table).update(query.data)

            # Apply filters with validation
            for key, value in query.filters.items():
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    return {
                        "success": False,
                        "error": f"Invalid filter column name: {key}",
                        "data": None,
                    }
                supabase_query = supabase_query.eq(key, value)

            response = supabase_query.execute()

            return {
                "success": True,
                "error": None,
                "data": response.data,
                "count": len(response.data),
            }

        except Exception as e:
            logger.error(f"Update query failed: {e}")
            return {"success": False, "error": str(e), "data": None}

    async def _handle_delete(self, query: DatabaseQuery) -> Dict[str, Any]:
        """Handle DELETE operations with strict security"""
        try:
            if not query.filters:
                return {
                    "success": False,
                    "error": "No filters provided for delete (safety check)",
                    "data": None,
                }

            # Additional safety check - require specific ID or multiple filters
            if len(query.filters) == 1 and "id" not in query.filters:
                return {
                    "success": False,
                    "error": "Delete operations require ID filter or multiple conditions",
                    "data": None,
                }

            # Build delete query
            supabase_query = self.client.table(query.table).delete()

            # Apply filters with validation
            for key, value in query.filters.items():
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    return {
                        "success": False,
                        "error": f"Invalid filter column name: {key}",
                        "data": None,
                    }
                supabase_query = supabase_query.eq(key, value)

            response = supabase_query.execute()

            return {
                "success": True,
                "error": None,
                "data": response.data,
                "count": len(response.data),
            }

        except Exception as e:
            logger.error(f"Delete query failed: {e}")
            return {"success": False, "error": str(e), "data": None}

    async def vector_search(self, search_query: VectorSearchQuery) -> Dict[str, Any]:
        """Perform vector similarity search with enhanced security"""
        try:
            if not self.connection_pool:
                return {
                    "success": False,
                    "error": "Direct database connection not available",
                    "data": None,
                }

            # Validate table name
            if search_query.table not in self.allowed_tables:
                return {
                    "success": False,
                    "error": f"Access denied to table: {search_query.table}",
                    "data": None,
                }

            # Generate embedding for search query
            embedding = await self._generate_embedding(search_query.query_text)
            if not embedding:
                return {
                    "success": False,
                    "error": "Failed to generate embedding",
                    "data": None,
                }

            # Build SQL query for vector search with parameterized queries
            sql = """
                SELECT 
                    id,
                    content,
                    metadata,
                    1 - (embedding <=> $1::vector) as similarity
                FROM document_embeddings
                WHERE 1 - (embedding <=> $1::vector) > $2
                ORDER BY embedding <=> $1::vector
                LIMIT $3
            """

            # Cap the limit
            limit = min(search_query.limit, 100)

            async with self.connection_pool.acquire() as conn:
                rows = await conn.fetch(
                    sql,
                    embedding,
                    search_query.similarity_threshold,
                    limit,
                )

            # Convert to list of dicts
            results = [dict(row) for row in rows]

            return {
                "success": True,
                "error": None,
                "data": results,
                "count": len(results),
            }

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return {"success": False, "error": "Vector search failed", "data": None}

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using LiteLLM proxy with retry logic"""
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                litellm_url = os.getenv(
                    "LITELLM_PROXY_URL", "http://litellm-proxy:4000"
                )

                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{litellm_url}/embeddings",
                        json={
                            "model": self.config.embedding_model,
                            "input": text[:8000],
                        },  # Limit text length
                        headers={
                            "Authorization": f"Bearer {os.getenv('LITELLM_MASTER_KEY', '')}"
                        },
                    )

                    if response.status_code == 200:
                        data = response.json()
                        return data["data"][0]["embedding"]
                    else:
                        logger.error(
                            f"Embedding generation failed (attempt {attempt + 1}): {response.text}"
                        )
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (attempt + 1))
                        continue

            except Exception as e:
                logger.error(f"Embedding generation error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                continue

        return None

    async def upsert_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert content with automatic embedding generation and validation"""
        try:
            # Validate input data
            if not isinstance(content_data, dict):
                return {
                    "success": False,
                    "error": "Content data must be a dictionary",
                    "data": None,
                }

            # Extract text content for embedding
            text_content = content_data.get("content", "")
            if not text_content or not isinstance(text_content, str):
                return {
                    "success": False,
                    "error": "No valid content provided for embedding",
                    "data": None,
                }

            # Limit content size
            if len(text_content) > 50000:  # 50KB limit
                text_content = text_content[:50000]
                logger.warning("Content truncated to 50KB for embedding generation")

            # Generate embedding
            embedding = await self._generate_embedding(text_content)
            if not embedding:
                return {
                    "success": False,
                    "error": "Failed to generate embedding",
                    "data": None,
                }

            # Prepare upsert data with validation
            upsert_data = {
                "content": text_content,
                "embedding": embedding,
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Add other fields if provided and valid
            allowed_fields = {"id", "title", "source", "metadata", "document_type"}
            for key, value in content_data.items():
                if key in allowed_fields and key not in upsert_data:
                    upsert_data[key] = value

            # Generate ID if not provided
            if "id" not in upsert_data:
                content_hash = hashlib.md5(text_content.encode()).hexdigest()
                upsert_data["id"] = f"content_{content_hash}"

            # Perform upsert
            response = (
                self.client.table("document_embeddings")
                .upsert(upsert_data, on_conflict="id")
                .execute()
            )

            return {
                "success": True,
                "error": None,
                "data": response.data,
                "count": len(response.data),
            }

        except Exception as e:
            logger.error(f"Content upsert failed: {e}")
            return {"success": False, "error": "Content upsert failed", "data": None}

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive agent health status"""
        try:
            # Test basic connectivity
            response = (
                self.client.table("video_transcriptions")
                .select("id")
                .limit(1)
                .execute()
            )

            pool_status = "unavailable"
            pool_stats = {}
            if self.connection_pool:
                pool_stats = {
                    "size": self.connection_pool.get_size(),
                    "max_size": self.connection_pool.get_max_size(),
                    "min_size": self.connection_pool.get_min_size(),
                    "idle": self.connection_pool.get_idle_size(),
                }
                pool_status = f"active ({pool_stats['size']}/{pool_stats['max_size']})"

            return {
                "status": self.status,
                "supabase_connection": "healthy" if response else "unhealthy",
                "connection_pool": pool_status,
                "pool_stats": pool_stats,
                "allowed_tables": list(self.allowed_tables),
                "rate_limit_config": {
                    "requests_per_minute": self.config.rate_limit_requests,
                    "max_query_size": self.config.max_query_size,
                },
                "active_clients": len(self.request_counts),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.connection_pool:
                await self.connection_pool.close()
            self.status = "stopped"
            logger.info("SupabaseAgent cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Factory function for creating SupabaseAgent
def create_supabase_agent(config_dict: Dict[str, Any]) -> SupabaseAgent:
    """Create a SupabaseAgent instance from configuration"""
    config = SupabaseConfig(**config_dict)
    return SupabaseAgent(config)
