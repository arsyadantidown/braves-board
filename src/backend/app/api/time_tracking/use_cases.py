import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.redis import redis_client
from app.api.task.repository import TaskRepository
from app.api.time_tracking.repository import TimeLogRepository
from app.api.time_tracking.schema import TimeLogCreate
from app.api.exceptions.task_exceptions import TaskNotFoundException
from app.api.exceptions.time_tracking_exceptions import (
    TimerAlreadyRunningException,
    TimerNotRunningException,
    TimerStateLostException,
    TimerNotActiveException
)

class TimeTrackingUseCase:
    def __init__(self, session: AsyncSession):
        self.task_repo = TaskRepository(session)
        self.time_log_repo = TimeLogRepository(session)

    def _get_key(self, task_id: uuid.UUID):
        return f"task:{task_id}:timer"

    async def start_timer(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        description: str | None = None
    ):
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException()

        if task.is_timer_running:
            raise TimerAlreadyRunningException()

        now = datetime.now(timezone.utc)
        key = self._get_key(task_id)

        await redis_client.hset(key, mapping={
            "start_time": now.isoformat(),
            "last_ping": now.isoformat(),
            "last_confirm": now.isoformat(),
            "description": description or ""
        })

        await self.time_log_repo.create(
            TimeLogCreate(
                task_id=task_id,
                start_time=now,
                activity_description=description
            ),
            user_id=user_id,
        )

        await self.task_repo.update(task_id, {
            "is_timer_running": True,
            "start_time": now
        })

        return {
            "message": "Timer berhasil dimulai",
            "task_id": str(task_id),
            "start_time": now,
            "description": description
        }

    async def stop_timer(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        reason: str = "manual"
    ):
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException()

        if not task.is_timer_running:
            raise TimerNotRunningException()

        key = self._get_key(task_id)
        data = await redis_client.hgetall(key)

        if not data:
            raise TimerStateLostException()

        data = {
            (k.decode() if isinstance(k, bytes) else k):
            (v.decode() if isinstance(v, bytes) else v)
            for k, v in data.items()
        }

        start_time = datetime.fromisoformat(data["start_time"])

        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        duration = int((now - start_time).total_seconds())
        new_total = (task.total_duration or 0) + duration

        logs = await self.time_log_repo.get_all_by_task_id(
            task_id,
            user_id,
        )

        if logs:
            last_log = logs[-1]

            if last_log.stop_time is None:
                await self.time_log_repo.update(
                    last_log.id,
                    {
                        "stop_time": now,
                        "duration_seconds": int(
                            (now - last_log.start_time).total_seconds()
                        ),
                        "stop_reason": reason
                    },
                    user_id,
                )

        await self.task_repo.update(task_id, {
            "is_timer_running": False,
            "start_time": None,
            "total_duration": new_total
        })

        await redis_client.delete(key)

        return {
            "message": "Timer berhasil dihentikan",
            "task_id": str(task_id),
            "duration_added": duration,
            "total_duration": new_total,
            "stopped_at": now
        }

    async def ping(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID
    ):
        key = self._get_key(task_id)
        data = await redis_client.hgetall(key)

        if not data:
            raise TimerNotActiveException()

        data = {
            (k.decode() if isinstance(k, bytes) else k):
            (v.decode() if isinstance(v, bytes) else v)
            for k, v in data.items()
        }

        now = datetime.now(timezone.utc)

        last_ping = datetime.fromisoformat(data["last_ping"])

        if last_ping.tzinfo is None:
            last_ping = last_ping.replace(tzinfo=timezone.utc)

        last_confirm = datetime.fromisoformat(data["last_confirm"])

        if last_confirm.tzinfo is None:
            last_confirm = last_confirm.replace(tzinfo=timezone.utc)

        if now - last_ping > timedelta(minutes=5):
            await self.stop_timer(
                task_id,
                user_id,
                reason="unexpected_close"
            )

            return {
                "message": "Timer otomatis dihentikan karena tidak ada aktivitas ping"
            }

        if now - last_confirm > timedelta(minutes=10):
            await self.stop_timer(
                task_id,
                user_id,
                reason="no_response"
            )

            return {
                "message": "Timer otomatis dihentikan karena tidak ada konfirmasi pengguna"
            }

        await redis_client.hset(
            key,
            "last_ping",
            now.isoformat()
        )

        return {
            "message": "Ping timer berhasil diperbarui",
            "task_id": str(task_id),
            "last_ping": now
        }

    async def confirm(self, task_id: uuid.UUID):
        key = self._get_key(task_id)
        exists = await redis_client.exists(key)

        if not exists:
            raise TimerNotActiveException()

        now = datetime.now(timezone.utc)

        await redis_client.hset(
            key,
            "last_confirm",
            now.isoformat()
        )

        return {
            "message": "Timer berhasil dikonfirmasi",
            "task_id": str(task_id),
            "last_confirm": now
        }

    async def get_time_logs(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ):
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException()

        logs = await self.time_log_repo.get_all_by_task_id(
            task_id,
            user_id,
        )

        return {
            "task_id": str(task_id),
            "count": len(logs),
            "logs": [
                {
                    "id": str(log.id),
                    "user_id": log.user_id,
                    "start_time": log.start_time,
                    "stop_time": log.stop_time,
                    "duration_seconds": log.duration_seconds,
                    "activity_description": log.activity_description,
                    "stop_reason": log.stop_reason,
                    "created_at": log.created_at
                }
                for log in logs
            ]
        }

    async def update_time_log(
        self,
        task_id: uuid.UUID,
        log_id: uuid.UUID,
        user_id: uuid.UUID,
        start_time: datetime | None = None,
        stop_time: datetime | None = None,
        activity_description: str | None = None,
    ):
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException()

        log = await self.time_log_repo.get_by_id(
            log_id,
            user_id,
        )

        if not log or log.task_id != task_id:
            raise TaskNotFoundException()

        update_data = {}

        log_start_time = (
            start_time
            if start_time is not None
            else log.start_time
        )

        if start_time is not None:
            update_data["start_time"] = start_time

        if stop_time is not None:
            update_data["stop_time"] = stop_time
            update_data["duration_seconds"] = max(
                0,
                int(
                    (stop_time - log_start_time).total_seconds()
                )
            )

        if activity_description is not None:
            update_data["activity_description"] = activity_description

        updated_log = await self.time_log_repo.update(
            log_id,
            update_data,
            user_id,
        )

        if not updated_log:
            raise TaskNotFoundException()

        return {
            "id": updated_log.id,
            "start_time": updated_log.start_time,
            "stop_time": updated_log.stop_time,
            "duration_seconds": updated_log.duration_seconds,
            "activity_description": updated_log.activity_description,
            "stop_reason": updated_log.stop_reason,
            "created_at": updated_log.created_at,
        }

    async def delete_time_log(
        self,
        task_id: uuid.UUID,
        log_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException()

        log = await self.time_log_repo.get_by_id(
            log_id,
            user_id,
        )

        if not log or log.task_id != task_id:
            raise TaskNotFoundException()

        deleted = await self.time_log_repo.delete(
            log_id,
            user_id,
        )

        if not deleted:
            raise TaskNotFoundException()

        return None

    async def run_cleanup(self):
        keys = await redis_client.keys("task:*:timer")
        now = datetime.now(timezone.utc)

        cleaned = 0
        stopped = []

        max_inactive_seconds = 300
        max_session_seconds = 43200

        for key in keys:
            data = await redis_client.hgetall(key)

            if not data:
                continue

            data = {
                (k.decode() if isinstance(k, bytes) else k):
                (v.decode() if isinstance(v, bytes) else v)
                for k, v in data.items()
            }

            key_str = key.decode() if isinstance(key, bytes) else key

            try:
                task_id_str = key_str.split(":")[1]
                task_id = uuid.UUID(task_id_str)
            except (IndexError, ValueError):
                continue

            last_ping = datetime.fromisoformat(
                data.get("last_ping", now.isoformat())
            )

            if last_ping.tzinfo is None:
                last_ping = last_ping.replace(
                    tzinfo=timezone.utc
                )

            start_time = datetime.fromisoformat(
                data.get("start_time", now.isoformat())
            )

            if start_time.tzinfo is None:
                start_time = start_time.replace(
                    tzinfo=timezone.utc
                )

            inactive_duration = (
                now - last_ping
            ).total_seconds()

            total_duration = (
                now - start_time
            ).total_seconds()

            if (
                inactive_duration > max_inactive_seconds
                or total_duration > max_session_seconds
            ):
                task = await self.task_repo.get_by_id(task_id)

                if task:
                    duration = int(
                        (now - start_time).total_seconds()
                    )

                    new_total = (
                        task.total_duration or 0
                    ) + duration

                    logs = await self.time_log_repo.get_all_by_task_id(
                        task_id
                    )

                    if logs:
                        last_log = logs[-1]

                        if last_log.stop_time is None:
                            await self.time_log_repo.update(
                                last_log.id,
                                {
                                    "stop_time": now,
                                    "duration_seconds": int(
                                        (now - last_log.start_time).total_seconds()
                                    ),
                                    "stop_reason": "unexpected_close"
                                }
                            )

                    await self.task_repo.update(task_id, {
                        "is_timer_running": False,
                        "start_time": None,
                        "total_duration": new_total
                    })

                await redis_client.delete(key)

                cleaned += 1
                stopped.append(str(task_id))

        return {
            "cleaned_sessions": cleaned,
            "stopped_tasks": stopped
        }