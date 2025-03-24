import time
import logging
import functools
from typing import Optional
from datetime import datetime

class CustomLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if none exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str, exc_info: Optional[Exception] = None):
        self.logger.error(message, exc_info=exc_info)

    def warning(self, message: str):
        self.logger.warning(message)

    def debug(self, message: str):
        self.logger.debug(message)

class PerformanceMonitor:
    def __init__(self, logger: CustomLogger):
        self.logger = logger
        self.timers = {}

    def start_timer(self, name: str):
        self.timers[name] = time.time()

    def stop_timer(self, name: str) -> float:
        if name not in self.timers:
            self.logger.warning(f"Timer {name} was not started")
            return 0.0
        
        duration = time.time() - self.timers[name]
        del self.timers[name]
        self.logger.info(f"{name} took {duration:.2f} seconds")
        return duration

def async_timer(logger: CustomLogger):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{func.__name__} completed in {duration:.2f} seconds")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed after {duration:.2f} seconds: {str(e)}",
                    exc_info=e
                )
                raise
        return wrapper
    return decorator 