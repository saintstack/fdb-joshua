"""
Logging utilities for Joshua.

This module provides centralized logging configuration and utilities
for consistent logging across the Joshua system.
"""

import logging
import logging.handlers
import sys
import time
import functools
from typing import Optional, Any, Callable
from contextlib import contextmanager
from ..core.config import config
from ..core.constants import LOG_FORMAT, LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT


# Module-level logger cache
_loggers = {}


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    log_to_file: bool = True
) -> None:
    """
    Set up logging configuration for Joshua.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        log_to_console: If True, log to console
        log_to_file: If True, log to file
    """
    # Use config defaults if not specified
    log_level = log_level or config.log_level
    log_file = log_file or config.log_file
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(config.log_format)
    
    # Add console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        root_logger.addHandler(console_handler)
    
    # Add file handler
    if log_to_file and log_file:
        try:
            # Ensure log directory exists
            import os
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=config.log_max_bytes,
                backupCount=config.log_backup_count
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, log_level.upper()))
            root_logger.addHandler(file_handler)
        except Exception as e:
            # Fall back to console only if file logging fails
            print(f"Warning: Could not set up file logging: {e}", file=sys.stderr)


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]


def log_exception(
    logger: logging.Logger,
    message: str = "An exception occurred",
    exc_info: bool = True
) -> None:
    """
    Log an exception with traceback.
    
    Args:
        logger: Logger instance
        message: Error message
        exc_info: If True, include exception info
    """
    logger.error(message, exc_info=exc_info)


@contextmanager
def log_performance(
    logger: logging.Logger,
    operation: str,
    level: int = logging.DEBUG
):
    """
    Context manager to log operation performance.
    
    Args:
        logger: Logger instance
        operation: Description of operation
        level: Logging level for the message
        
    Example:
        >>> with log_performance(logger, "database query"):
        ...     result = db.query()
    """
    start_time = time.time()
    logger.log(level, f"Starting {operation}")
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.log(level, f"Completed {operation} in {duration:.3f}s")


def log_function_call(
    logger: Optional[logging.Logger] = None,
    level: int = logging.DEBUG,
    include_args: bool = True,
    include_result: bool = False
) -> Callable:
    """
    Decorator to log function calls.
    
    Args:
        logger: Logger instance (uses function's module logger if None)
        level: Logging level
        include_args: If True, log function arguments
        include_result: If True, log function result
        
    Returns:
        Decorator function
        
    Example:
        >>> @log_function_call(include_result=True)
        ... def process_data(data):
        ...     return len(data)
    """
    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Build log message
            func_name = func.__name__
            if include_args:
                args_str = ', '.join(
                    [repr(arg) for arg in args] +
                    [f"{k}={repr(v)}" for k, v in kwargs.items()]
                )
                logger.log(level, f"Calling {func_name}({args_str})")
            else:
                logger.log(level, f"Calling {func_name}")
            
            # Call function
            try:
                result = func(*args, **kwargs)
                
                if include_result:
                    logger.log(level, f"{func_name} returned {repr(result)}")
                else:
                    logger.log(level, f"{func_name} completed successfully")
                
                return result
                
            except Exception as e:
                logger.error(f"{func_name} failed with {type(e).__name__}: {e}")
                raise
        
        return wrapper
    return decorator


class LogAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds context to log messages.
    
    Example:
        >>> logger = get_logger(__name__)
        >>> adapter = LogAdapter(logger, {'ensemble_id': '12345'})
        >>> adapter.info("Processing")  # Logs: Processing [ensemble_id=12345]
    """
    
    def process(self, msg: str, kwargs: dict) -> tuple:
        """Add context to log message."""
        if self.extra:
            context = ' '.join(f'{k}={v}' for k, v in self.extra.items())
            msg = f"{msg} [{context}]"
        return msg, kwargs


def create_context_logger(
    logger: logging.Logger,
    **context
) -> LogAdapter:
    """
    Create a logger with additional context.
    
    Args:
        logger: Base logger
        **context: Context key-value pairs
        
    Returns:
        LogAdapter with context
        
    Example:
        >>> logger = get_logger(__name__)
        >>> ctx_logger = create_context_logger(logger, user='alice', job='123')
        >>> ctx_logger.info("Started")  # Logs: Started [user=alice job=123]
    """
    return LogAdapter(logger, context)


class ProgressLogger:
    """
    Logger for tracking progress of long-running operations.
    
    Example:
        >>> progress = ProgressLogger(logger, "Processing files", total=100)
        >>> for i, file in enumerate(files):
        ...     process(file)
        ...     progress.update(i + 1)
        >>> progress.complete()
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        total: Optional[int] = None,
        report_interval: int = 10
    ):
        """
        Initialize progress logger.
        
        Args:
            logger: Logger instance
            operation: Description of operation
            total: Total number of items (if known)
            report_interval: Progress reporting interval (seconds)
        """
        self.logger = logger
        self.operation = operation
        self.total = total
        self.report_interval = report_interval
        self.current = 0
        self.start_time = time.time()
        self.last_report_time = self.start_time
        
        self.logger.info(f"Starting {operation}" + 
                        (f" (total: {total})" if total else ""))
    
    def update(self, current: int, message: Optional[str] = None) -> None:
        """
        Update progress.
        
        Args:
            current: Current progress count
            message: Optional progress message
        """
        self.current = current
        now = time.time()
        
        # Check if we should report
        if now - self.last_report_time >= self.report_interval:
            self._report_progress(message)
            self.last_report_time = now
    
    def _report_progress(self, message: Optional[str] = None) -> None:
        """Report current progress."""
        elapsed = time.time() - self.start_time
        rate = self.current / elapsed if elapsed > 0 else 0
        
        progress_msg = f"{self.operation}: {self.current}"
        if self.total:
            percent = (self.current / self.total) * 100
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            progress_msg += f"/{self.total} ({percent:.1f}%)"
            progress_msg += f" - Rate: {rate:.1f}/s"
            progress_msg += f" - ETA: {remaining:.0f}s"
        else:
            progress_msg += f" items - Rate: {rate:.1f}/s"
        
        if message:
            progress_msg += f" - {message}"
        
        self.logger.info(progress_msg)
    
    def complete(self, message: Optional[str] = None) -> None:
        """Mark operation as complete."""
        elapsed = time.time() - self.start_time
        complete_msg = f"Completed {self.operation}: {self.current} items in {elapsed:.1f}s"
        
        if message:
            complete_msg += f" - {message}"
        
        self.logger.info(complete_msg)


# Initialize logging on module import
setup_logging()