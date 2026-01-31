"""
SEAA Structured Logging

Production-ready logging with:
- JSON format for production (machine-readable)
- Colored console format for development (human-readable)
- Context-aware logging with module names
- Log levels properly configured
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Optional


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production/log aggregation."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "levelname", "levelno",
                "pathname", "filename", "module", "exc_info", "exc_text",
                "stack_info", "lineno", "funcName", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message"
            ):
                log_data[key] = value
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for development."""
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Component colors
    COMPONENT_COLORS = {
        "GENESIS": "\033[95m",    # Light magenta
        "ARCHITECT": "\033[94m",  # Light blue
        "GATEWAY": "\033[96m",    # Light cyan
        "BUS": "\033[92m",        # Light green
        "IMMUNITY": "\033[93m",   # Light yellow
        "ASSIMILATOR": "\033[91m", # Light red
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Get the color for this log level
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Extract component from logger name
        component = record.name.split(".")[-1].upper()
        component_color = self.COMPONENT_COLORS.get(component, "\033[37m")
        
        # Format the timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Build the formatted message
        level = f"{color}{record.levelname:8}{self.RESET}"
        logger = f"{component_color}[{component:12}]{self.RESET}"
        message = record.getMessage()
        
        formatted = f"{timestamp} {level} {logger} {message}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(
    level: str = "INFO",
    format_type: str = "colored",
    log_file: Optional[str] = None
) -> None:
    """
    Configure the root logger for SEAA.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 'json' for production, 'colored' for development
        log_file: Optional file path to write logs
    """
    root_logger = logging.getLogger("seaa")
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if format_type == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)

    # Optional file handler (always JSON for parsing)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    # Optional remote handler (with sanitization)
    try:
        from seaa.core.remote_logging import setup_remote_logging
        setup_remote_logging()
    except Exception as e:
        # Don't crash if remote logging fails to initialize
        pass

    # Prevent propagation to root logger
    root_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific component.
    
    Args:
        name: Component name (e.g., 'genesis', 'architect')
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"seaa.{name}")


class LogContext:
    """Context manager for adding extra fields to log messages."""
    
    def __init__(self, logger: logging.Logger, **context: Any):
        self.logger = logger
        self.context = context
        self._old_factory = None
    
    def __enter__(self):
        self._old_factory = logging.getLogRecordFactory()
        extra = self.context
        
        def factory(*args, **kwargs):
            record = self._old_factory(*args, **kwargs)
            for key, value in extra.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(factory)
        return self
    
    def __exit__(self, *args):
        logging.setLogRecordFactory(self._old_factory)


# Initialize with colored output by default (development mode)
# Will be reconfigured by config.py on startup
setup_logging(level="DEBUG", format_type="colored")
