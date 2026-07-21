from fastapi import APIRouter

from app.api.auth.views import router as auth_router
from app.api.board.views import router as board_router
from app.api.column.views import router as column_router
from app.api.task.views import router as task_router
from app.api.subtask.views import router as subtask_router
from app.api.task_comment.views import router as task_comment_router
from app.api.task_attachment.views import router as task_attachment_router
from app.api.user.views import router as user_router
from app.api.time_tracking.views import router as time_tracking_router
from app.api.log.views import router as log_router
from app.api.board_member.views import router as board_member_router
from app.api.notification.views import router as notification_router
api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(board_router)
api_router.include_router(column_router)
api_router.include_router(task_router)
api_router.include_router(subtask_router)
api_router.include_router(task_comment_router)
api_router.include_router(task_attachment_router)
api_router.include_router(user_router)
api_router.include_router(time_tracking_router)
api_router.include_router(log_router)
api_router.include_router(board_member_router)
api_router.include_router(notification_router)