"""
SEAA CLI Runtime Manager

Manages Genesis execution in a background thread for interactive CLI use.
"""

import threading
import time
from typing import Optional, Callable

from seaa.core.logging import get_logger

logger = get_logger("cli.runtime")


class GenesisRuntime:
    """
    Manages Genesis lifecycle for interactive CLI.

    Runs Genesis in a daemon thread so it can:
    - Start on command
    - Stop gracefully
    - Be monitored while running
    - Not block the REPL

    Thread safety: All public methods are thread-safe.
    """

    def __init__(self):
        self._genesis = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._stop_requested = False
        self._error: Optional[Exception] = None

        # Callbacks
        self._on_start: Optional[Callable[[], None]] = None
        self._on_stop: Optional[Callable[[], None]] = None
        self._on_error: Optional[Callable[[Exception], None]] = None

    def is_running(self) -> bool:
        """Check if Genesis is currently running."""
        with self._lock:
            return self._running and self._thread is not None and self._thread.is_alive()

    def get_error(self) -> Optional[Exception]:
        """Get last error if any."""
        with self._lock:
            return self._error

    def start(self) -> bool:
        """
        Start Genesis in a background thread.

        Returns:
            True if started successfully, False if already running
        """
        with self._lock:
            if self._running or (self._thread and self._thread.is_alive()):
                logger.warning("Genesis already running")
                return False

            self._stop_requested = False
            self._error = None
            self._running = True

            self._thread = threading.Thread(
                target=self._run_genesis,
                name="genesis-runtime",
                daemon=True,  # Daemon thread exits when main thread exits
            )
            self._thread.start()

            logger.info("Genesis thread started")

            if self._on_start:
                try:
                    self._on_start()
                except Exception as e:
                    logger.warning(f"on_start callback error: {e}")

            return True

    def stop(self, timeout: float = 10.0) -> bool:
        """
        Stop Genesis gracefully.

        Args:
            timeout: Maximum time to wait for shutdown

        Returns:
            True if stopped successfully
        """
        with self._lock:
            if not self._running:
                logger.debug("Genesis not running")
                return True

            self._stop_requested = True

            # Signal Genesis to stop
            if self._genesis:
                self._genesis._running = False

        # Wait outside lock
        if self._thread:
            self._thread.join(timeout=timeout)

            if self._thread.is_alive():
                logger.warning("Genesis thread did not stop in time")
                return False

        with self._lock:
            self._running = False
            self._thread = None

            logger.info("Genesis stopped")

            if self._on_stop:
                try:
                    self._on_stop()
                except Exception as e:
                    logger.warning(f"on_stop callback error: {e}")

            return True

    def trigger_evolution(self) -> bool:
        """
        Trigger an evolution cycle.

        This signals Genesis to run an evolution cycle
        at the next opportunity.

        Returns:
            True if signal sent, False if Genesis not running
        """
        with self._lock:
            if not self._running or not self._genesis:
                return False

            # Genesis doesn't have a direct trigger, but we can
            # call architect.reflect() which will cause evolution
            # on the next metabolic cycle
            try:
                self._genesis.architect.reflect()
                return True
            except Exception as e:
                logger.error(f"Failed to trigger evolution: {e}")
                return False

    def _run_genesis(self) -> None:
        """Run Genesis in the background thread."""
        try:
            from seaa.kernel import Genesis
            from seaa.core.logging import setup_logging

            # Setup logging for background thread
            setup_logging(level="INFO", format_type="colored")

            logger.info("Creating Genesis instance...")
            self._genesis = Genesis()

            logger.info("Awakening Genesis...")
            self._genesis.awaken()

        except KeyboardInterrupt:
            logger.info("Genesis interrupted")
        except Exception as e:
            logger.error(f"Genesis error: {e}")
            with self._lock:
                self._error = e

            if self._on_error:
                try:
                    self._on_error(e)
                except Exception as callback_error:
                    logger.warning(f"on_error callback error: {callback_error}")

        finally:
            with self._lock:
                self._running = False
                self._genesis = None

            logger.info("Genesis thread exiting")

    def on_start(self, callback: Callable[[], None]) -> "GenesisRuntime":
        """Register callback for when Genesis starts."""
        self._on_start = callback
        return self

    def on_stop(self, callback: Callable[[], None]) -> "GenesisRuntime":
        """Register callback for when Genesis stops."""
        self._on_stop = callback
        return self

    def on_error(self, callback: Callable[[Exception], None]) -> "GenesisRuntime":
        """Register callback for Genesis errors."""
        self._on_error = callback
        return self


# Module-level singleton
_runtime: Optional[GenesisRuntime] = None
_runtime_lock = threading.Lock()


def get_runtime() -> GenesisRuntime:
    """Get the Genesis runtime singleton."""
    global _runtime
    if _runtime is None:
        with _runtime_lock:
            if _runtime is None:
                _runtime = GenesisRuntime()
    return _runtime


def start_genesis() -> bool:
    """Start Genesis in background."""
    return get_runtime().start()


def stop_genesis(timeout: float = 10.0) -> bool:
    """Stop Genesis gracefully."""
    return get_runtime().stop(timeout)


def is_genesis_running() -> bool:
    """Check if Genesis is running."""
    return get_runtime().is_running()
