import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.settings import settings


# Module-level handler singleton
_handler_instance: "TimescaleLogHandler | None" = None


class TimescaleLogHandler(logging.Handler):
    """
    Custom async logging handler that buffers log entries and bulk-inserts
    them into a TimescaleDB hypertable (app_logs).

    Uses asyncpg directly for high-performance batch inserts instead of
    SQLAlchemy ORM to avoid session overhead.
    """

    def __init__(
        self,
        database_url: str,
        buffer_size: int = 100,
        flush_interval: float = 5.0,
        level: int = logging.DEBUG,
    ):
        super().__init__(level=level)
        self._database_url = self._convert_to_asyncpg_url(database_url)
        self._buffer_size = buffer_size
        self._flush_interval = flush_interval
        self._buffer: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._pool = None
        self._flush_task: asyncio.Task | None = None
        self._started = False

    @staticmethod
    def _convert_to_asyncpg_url(url: str) -> str:
        """Convert SQLAlchemy async URL to asyncpg format."""
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url

    async def start(self) -> None:
        """Initialize the connection pool and start the periodic flush task."""
        if self._started:
            return

        import asyncpg
        self._pool = await asyncpg.create_pool(
            self._database_url,
            min_size=1,
            max_size=3,
        )
        self._flush_task = asyncio.create_task(self._periodic_flush())
        self._started = True

    async def stop(self) -> None:
        """Flush remaining buffer and close the connection pool."""
        if not self._started:
            return

        self._started = False

        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self._flush()

        if self._pool:
            await self._pool.close()
            self._pool = None

    def emit(self, record: logging.LogRecord) -> None:
        """
        Called by the logging framework. Enqueues the log record
        into the in-memory buffer. If the buffer is full, schedules
        an async flush.
        """
        if not self._started:
            return

        try:
            entry = self._record_to_dict(record)
            self._buffer.append(entry)

            if len(self._buffer) >= self._buffer_size:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(self._flush())
        except Exception:
            self.handleError(record)

    def _record_to_dict(self, record: logging.LogRecord) -> dict[str, Any]:
        """Convert a LogRecord to a dict matching the app_logs table schema."""
        extra = getattr(record, "log_extra", None) or {}
        log_type = getattr(record, "log_type", "application")

        # Parse user_id if present
        user_id_raw = extra.pop("user_id", None)
        user_id = None
        if user_id_raw:
            try:
                user_id = uuid.UUID(str(user_id_raw)) if not isinstance(user_id_raw, uuid.UUID) else user_id_raw
            except (ValueError, AttributeError):
                user_id = None

        return {
            "timestamp": datetime.now(timezone.utc),
            "log_type": str(log_type),
            "level": record.levelname,
            "logger_name": record.name,
            "message": self.format(record) if self.formatter else record.getMessage(),
            "user_id": user_id,
            "request_id": extra.pop("request_id", None),
            "method": extra.pop("method", None),
            "path": extra.pop("path", None),
            "status_code": extra.pop("status_code", None),
            "duration_ms": extra.pop("duration_ms", None),
            "ip_address": extra.pop("ip_address", None),
            "user_agent": extra.pop("user_agent", None),
            "action": extra.pop("action", None),
            "resource_type": extra.pop("resource_type", None),
            "resource_id": extra.pop("resource_id", None),
            "extra": json.dumps(extra) if extra else None,
        }

    async def _periodic_flush(self) -> None:
        """Periodically flush the buffer to the database."""
        while self._started:
            try:
                await asyncio.sleep(self._flush_interval)
                await self._flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.getLogger("timescale_handler").error(
                    f"Periodic flush error: {e}", exc_info=True
                )

    async def _flush(self) -> None:
        """Bulk-insert buffered log entries into the app_logs hypertable."""
        async with self._lock:
            if not self._buffer or not self._pool:
                return

            entries = self._buffer.copy()
            self._buffer.clear()

        try:
            async with self._pool.acquire() as conn:
                await conn.executemany(
                    """
                    INSERT INTO app_logs (
                        timestamp, log_type, level, logger_name, message,
                        user_id, request_id, method, path, status_code,
                        duration_ms, ip_address, user_agent, action,
                        resource_type, resource_id, extra
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                        $11, $12, $13, $14, $15, $16, $17
                    )
                    """,
                    [
                        (
                            e["timestamp"],
                            e["log_type"],
                            e["level"],
                            e["logger_name"],
                            e["message"],
                            e["user_id"],
                            e["request_id"],
                            e["method"],
                            e["path"],
                            e["status_code"],
                            e["duration_ms"],
                            e["ip_address"],
                            e["user_agent"],
                            e["action"],
                            e["resource_type"],
                            e["resource_id"],
                            e["extra"],
                        )
                        for e in entries
                    ],
                )
        except Exception as e:
            logging.getLogger("timescale_handler").error(
                f"Failed to flush {len(entries)} log entries: {e}",
                exc_info=True,
            )
            # Re-add entries to buffer for retry (capped to avoid memory issues)
            async with self._lock:
                remaining_capacity = self._buffer_size * 2 - len(self._buffer)
                if remaining_capacity > 0:
                    self._buffer = entries[:remaining_capacity] + self._buffer


def get_log_handler() -> TimescaleLogHandler | None:
    """Get the singleton handler instance."""
    return _handler_instance


async def setup_log_handler() -> TimescaleLogHandler:
    """Create and start the singleton TimescaleLogHandler."""
    global _handler_instance

    if _handler_instance is not None:
        return _handler_instance

    handler = TimescaleLogHandler(
        database_url=settings.DATABASE_URL,
        buffer_size=settings.LOG_BUFFER_SIZE,
        flush_interval=float(settings.LOG_FLUSH_INTERVAL_SECONDS),
        level=logging.DEBUG,
    )
    await handler.start()
    _handler_instance = handler

    # Attach handler to root logger so all app loggers are captured
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    return handler


async def shutdown_log_handler() -> None:
    """Stop and cleanup the singleton handler."""
    global _handler_instance

    if _handler_instance is not None:
        root_logger = logging.getLogger()
        root_logger.removeHandler(_handler_instance)
        await _handler_instance.stop()
        _handler_instance = None


async def audit_log(
    user_id: uuid.UUID | str | None = None,
    action: str = "",
    resource_type: str = "",
    resource_id: str = "",
    message: str = "",
    request_id: str | None = None,
    **extra_fields,
) -> None:
    """
    Convenience function to emit an audit log entry.

    Usage:
        from app.lib.logging import audit_log

        await audit_log(
            user_id=current_user.id,
            action="board.create",
            resource_type="board",
            resource_id=str(board.id),
            message=f"User created board '{board.name}'"
        )
    """
    logger = logging.getLogger("audit")

    log_record = logger.makeRecord(
        name="audit",
        level=logging.INFO,
        fn="",
        lno=0,
        msg=message,
        args=(),
        exc_info=None,
    )

    log_record.log_type = "audit"
    log_record.log_extra = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "request_id": request_id,
        **extra_fields,
    }

    logger.handle(log_record)
