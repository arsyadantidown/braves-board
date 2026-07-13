import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import update

from app.connections.redis import redis_client
from app.models.task_model import Task
from app.api.board.schema import BoardCreate
from app.api.board.repository import BoardRepository
from app.api.column.repository import ColumnRepository
from app.api.task.repository import TaskRepository
from app.api.time_tracking.repository import TimeLogRepository
from app.api.exceptions.board_exceptions import BoardNotFoundException, InvalidBoardUpdateException
from app.api.board_member.repository import BoardMemberRepository
from app.models.board_member_model import BoardRole


class BoardUseCase:
    def __init__(self, repo: BoardRepository, session):
        self.repo = repo
        self.session = session
        self.column_repo = ColumnRepository(session)
        self.task_repo = TaskRepository(session)
        self.time_log_repo = TimeLogRepository(session)
        self.board_member_repo = BoardMemberRepository(session)

    def _board_to_dict(self, board):
        return {
            "id": str(board.id),
            "title": board.title,
            "user_id": str(board.user_id),
            "created_at": board.created_at,
            "updated_at": board.updated_at,
        }

    async def _lazy_hook(self, user_id: uuid.UUID) -> str:
        key = f"user:{user_id}:last_ping"
        last_ping = await redis_client.get(key)

        if not last_ping:
            return "offline"

        try:
            if isinstance(last_ping, bytes):
                last_ping = last_ping.decode()
            last_ping = datetime.fromisoformat(last_ping)
        except Exception:
            return "offline"

        if last_ping.tzinfo is None:
            last_ping = last_ping.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        diff = (now - last_ping).total_seconds()

        if diff > 3 * 3600:
            return "offline"
        elif diff > 5 * 60:
            return "idle"

        return "online"

    async def _sync_lazy_timers(self, tasks):
        now = datetime.now(timezone.utc)
        
        for task in tasks:
            if not getattr(task, "is_timer_running", False):
                continue

            key = f"task:{task.id}:timer"
            data = await redis_client.hgetall(key)

            should_stop = False
            stop_reason = ""
            stop_time = now
            start_time = getattr(task, "start_time", None) or now
            
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)

            if not data:
                should_stop = True
                stop_reason = "redis_data_lost"
            else:
                data = {
                    (k.decode() if isinstance(k, bytes) else k):
                    (v.decode() if isinstance(v, bytes) else v)
                    for k, v in data.items()
                }

                last_ping = datetime.fromisoformat(data.get("last_ping", now.isoformat()))
                last_confirm = datetime.fromisoformat(data.get("last_confirm", now.isoformat()))
                redis_start = datetime.fromisoformat(data.get("start_time", start_time.isoformat()))

                if last_ping.tzinfo is None: last_ping = last_ping.replace(tzinfo=timezone.utc)
                if last_confirm.tzinfo is None: last_confirm = last_confirm.replace(tzinfo=timezone.utc)
                if redis_start.tzinfo is None: redis_start = redis_start.replace(tzinfo=timezone.utc)
                
                start_time = redis_start
                ping_diff = (now - last_ping).total_seconds()
                confirm_diff = (now - last_confirm).total_seconds()

                if ping_diff > 5 * 60:
                    should_stop = True
                    stop_reason = "unexpected_close"
                    stop_time = last_ping
                elif confirm_diff > 3 * 3600:
                    should_stop = True
                    stop_reason = "no_response"
                    stop_time = start_time + timedelta(hours=3)

            if should_stop:
                duration = int((stop_time - start_time).total_seconds())
                if duration < 0:
                    duration = 0

                stmt = (
                    update(Task)
                    .where(Task.id == task.id, Task.is_timer_running == True)
                    .values(
                        is_timer_running=False,
                        start_time=None,
                        total_duration=Task.total_duration + duration
                    )
                    .returning(Task.id)
                )
                result = await self.session.execute(stmt)
                updated_task_id = result.scalar_one_or_none()

                if updated_task_id:
                    logs = await self.time_log_repo.get_all_by_task_id(task.id)
                    if logs:
                        last_log = logs[-1]
                        if last_log.stop_time is None:
                            await self.time_log_repo.update(last_log.id, {
                                "stop_time": stop_time,
                                "duration_seconds": int((stop_time - last_log.start_time).total_seconds()),
                                "stop_reason": stop_reason
                            })
                    await self.session.commit()

                await redis_client.delete(key)

                task.is_timer_running = False
                task.total_duration = (getattr(task, "total_duration", 0) or 0) + duration

    async def get_all(self, user_id: uuid.UUID, limit: int = 10, offset: int = 0):
        user_status = await self._lazy_hook(user_id)
        boards = await self.repo.get_all(user_id, limit, offset)

        return {
            "boards": [self._board_to_dict(b) for b in boards],
            "meta": {
                "limit": limit,
                "offset": offset,
                "count": len(boards),
                "status": user_status
            }
        }

    async def get_detail(self, board_id: uuid.UUID, user_id: uuid.UUID):
        user_status = await self._lazy_hook(user_id)
        board = await self.repo.get_by_id(board_id, user_id)
        
        if not board:
            raise BoardNotFoundException()

        columns = await self.column_repo.get_all_by_board_id(board_id)
        columns = columns or []

        tasks = await self.task_repo.get_all_by_board_id(board_id)
        tasks = tasks or []

        await self._sync_lazy_timers(tasks)

        tasks_by_column = {}
        for task in tasks:
            col_id = str(task.column_id)
            if col_id not in tasks_by_column:
                tasks_by_column[col_id] = []

            tasks_by_column[col_id].append({
                "id": str(task.id),
                "title": task.title,
                "column_id": str(task.column_id),
                "position": task.position,
                "is_timer_running": getattr(task, "is_timer_running", False),
                "total_duration": getattr(task, "total_duration", 0),
                "created_at": task.created_at,
                "updated_at": task.updated_at,
            })

        return {
            "board": {
                "id": str(board.id),
                "title": board.title,
                "user_id": str(board.user_id),
                "created_at": board.created_at,
                "updated_at": board.updated_at,
                "columns": [
                    {
                        "id": str(c.id),
                        "title": c.title,
                        "board_id": str(c.board_id),
                        "position": c.position,
                        "created_at": c.created_at,
                        "updated_at": c.updated_at,
                        "deleted_at": c.deleted_at,
                        "tasks": tasks_by_column.get(str(c.id), [])
                    }
                    for c in columns
                ]
            },
            "meta": {
                "has_columns": len(columns) > 0,
                "status": user_status
            }
        }

    async def create(self, board_in: BoardCreate, user_id: uuid.UUID):
        board = await self.repo.create(board_in, user_id)

        await self.board_member_repo.create(
            board_id=board.id,
            user_id=user_id,
            role=BoardRole.OWNER
        )

        return self._board_to_dict(board)

    async def update(self, board_id: uuid.UUID, update_data: dict, user_id: uuid.UUID):
        if not update_data:
            raise InvalidBoardUpdateException()

        board = await self.repo.update(board_id, update_data, user_id)
        if not board:
            raise BoardNotFoundException()

        return self._board_to_dict(board)

    async def delete(self, board_id: uuid.UUID, user_id: uuid.UUID):
        success = await self.repo.soft_delete(board_id, user_id)
        if not success:
            raise BoardNotFoundException()
        return None