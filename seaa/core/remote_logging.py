"""
SEAA Remote Logging

Secure remote logging handler with sanitization.
Logs are buffered and sent in batches to prevent spam.
Only high-priority logs (WARNING+) are sent by default.
"""

import json
import logging
import threading
import time
from typing import Optional, List, Dict, Any
from queue import Queue
from datetime import datetime

import requests

from seaa.core.config import config


class RemoteLoggingHandler(logging.Handler):
    """
    Logging handler that sends logs to a remote server with sanitization.

    Features:
    - Buffers logs in memory before sending
    - Sanitizes sensitive information before transmission
    - Only sends high-priority logs (WARNING+)
    - Runs in background thread to avoid blocking
    - Graceful shutdown with flush
    """

    def __init__(self, url: str, api_key: Optional[str] = None,
                 batch_size: int = 50, flush_interval: float = 10.0):
        """
        Initialize remote logging handler.

        Args:
            url: Remote server URL to POST logs to
            api_key: Optional API key for authentication
            batch_size: Buffer size before sending
            flush_interval: Seconds between flushes
        """
        super().__init__()
        self.url = url
        self.api_key = api_key
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self._queue: Queue = Queue()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self._start_worker()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        Sanitizes the record before queuing.
        """
        try:
            # Sanitize before queueing
            safe_record = self._sanitize_record(record)
            self._queue.put_nowait(safe_record)
        except Exception:
            # Don't raise exceptions from logging handlers
            self.handleError(record)

    def _sanitize_record(self, record: logging.LogRecord) -> Dict[str, Any]:
        """
        Sanitize a log record for remote transmission.

        Removes potentially sensitive information:
        - Full exception tracebacks
        - File paths
        - Function arguments
        - Detailed error messages

        Returns:
            Sanitized log record dict
        """
        # Only send high-priority logs
        if record.levelno < logging.WARNING:
            return {}

        return {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": self._sanitize_message(record.getMessage()),
            # Do NOT include: exc_info, exc_text, stack_info, args, funcName, filename
        }

    @staticmethod
    def _sanitize_message(message: str) -> str:
        """
        Sanitize a log message.

        Removes or masks:
        - API keys/URLs
        - File paths
        - Long stack traces
        - Sensitive patterns
        """
        if not message or not isinstance(message, str):
            return ""

        # Limit length
        message = message[:500]

        # Mask common sensitive patterns
        message = message.replace("http://", "http://...")
        message = message.replace("https://", "https://...")

        # Remove file paths (replace with <path>)
        import re
        message = re.sub(r"/[a-z0-9/_\-\.]+", "<path>", message, flags=re.IGNORECASE)
        message = re.sub(r"[A-Z]:[\\\/][a-z0-9_\-\.\\\/]+", "<path>", message, flags=re.IGNORECASE)

        # Remove potential API keys (long hex strings)
        message = re.sub(r"[a-f0-9]{32,}", "<key>", message)

        return message

    def _start_worker(self) -> None:
        """Start background worker thread."""
        if self._running:
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            name="remote-logging-worker",
            daemon=True,
        )
        self._worker_thread.start()

    def _worker_loop(self) -> None:
        """Background worker that batches and sends logs."""
        batch: List[Dict[str, Any]] = []
        last_send = time.time()

        while self._running:
            try:
                # Try to get log from queue (with timeout)
                timeout = max(0.1, self.flush_interval - (time.time() - last_send))
                try:
                    record = self._queue.get(timeout=timeout)
                    if record:  # Not empty
                        batch.append(record)
                except:
                    pass

                # Send if buffer full or timeout
                if len(batch) >= self.batch_size or (time.time() - last_send) > self.flush_interval:
                    if batch:
                        self._send_batch(batch)
                        batch = []
                        last_send = time.time()

            except Exception as e:
                # Log locally but don't crash worker
                print(f"Remote logging error: {e}", flush=True)
                time.sleep(1)

    def _send_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Send a batch of logs to remote server."""
        if not batch:
            return

        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            payload = {
                "logs": batch,
                "instance_id": self._get_instance_id(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

            response = requests.post(
                self.url,
                json=payload,
                headers=headers,
                timeout=5.0,
            )

            if not response.ok:
                print(f"Remote logging failed: {response.status_code}", flush=True)

        except Exception as e:
            print(f"Remote logging send error: {e}", flush=True)

    @staticmethod
    def _get_instance_id() -> str:
        """Get instance ID from identity system if available."""
        try:
            from seaa.kernel.identity import get_identity
            return get_identity().id
        except Exception:
            return "unknown"

    def flush(self) -> None:
        """Flush any pending logs."""
        super().flush()
        # Wait for queue to drain
        timeout = time.time() + 5.0
        while not self._queue.empty() and time.time() < timeout:
            time.sleep(0.1)

    def close(self) -> None:
        """Close handler and stop worker."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
        super().close()


def setup_remote_logging() -> Optional[RemoteLoggingHandler]:
    """
    Setup remote logging if enabled in config.

    Returns:
        RemoteLoggingHandler if enabled, None otherwise
    """
    remote_config = getattr(config, "remote_logging", None)
    if not remote_config:
        return None

    if not getattr(remote_config, "enabled", False):
        return None

    url = getattr(remote_config, "url", "")
    if not url:
        return None

    api_key = getattr(remote_config, "api_key", None)
    batch_size = getattr(remote_config, "batch_size", 50)
    flush_interval = getattr(remote_config, "flush_interval_seconds", 10)

    handler = RemoteLoggingHandler(
        url=url,
        api_key=api_key,
        batch_size=batch_size,
        flush_interval=flush_interval,
    )

    # Get root logger and add handler
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    return handler
