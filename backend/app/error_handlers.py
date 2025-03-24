from enum import Enum
from typing import Dict, Any, Optional
import asyncio

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecoveryStrategy:
    MAX_RETRIES = 3
    BACKOFF_BASE = 2  # exponential backoff base

    @staticmethod
    async def handle_audio_processing_error(error_details: Dict[str, Any], audio_processor: Any) -> bool:
        """
        Handle audio processing errors with recovery attempts.
        Returns True if recovery should be attempted, False otherwise.
        """
        error_type = error_details.get("error_type", "")
        retry_count = error_details.get("context", {}).get("retry_count", 0)

        if retry_count >= RecoveryStrategy.MAX_RETRIES:
            return False

        # Add exponential backoff delay
        await asyncio.sleep(RecoveryStrategy.BACKOFF_BASE ** retry_count)

        # Reset audio processor if possible
        if hasattr(audio_processor, 'reset'):
            await audio_processor.reset()

        return True

    @staticmethod
    async def handle_api_connection_error(error_details: Dict[str, Any], retry_count: int) -> bool:
        """
        Handle API connection errors with recovery attempts.
        Returns True if recovery should be attempted, False otherwise.
        """
        if retry_count >= RecoveryStrategy.MAX_RETRIES:
            return False

        # Add exponential backoff delay
        await asyncio.sleep(RecoveryStrategy.BACKOFF_BASE ** retry_count)
        return True

class TranscriptionErrorHandler:
    @staticmethod
    def handle_error(
        error_type: str,
        exception: Exception = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        message: str = None,
        **additional_context
    ) -> Dict[str, Any]:
        """
        Handle errors in a standardized way across the application.
        """
        error_details = {
            "error_type": error_type,
            "message": message or str(exception) if exception else "Unknown error",
            "severity": severity.value,
            "context": additional_context
        }
        
        # Add stack trace in development mode
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] and exception:
            import traceback
            error_details["stack_trace"] = traceback.format_exc()
        
        return error_details 