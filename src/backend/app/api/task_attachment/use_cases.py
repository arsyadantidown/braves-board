import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.task.repository import TaskRepository

from app.api.task_attachment.schema import TaskAttachmentCreate
from app.api.task_attachment.repository import TaskAttachmentRepository

from app.api.notification.repository import NotificationRepository
from app.api.notification.use_cases import NotificationUseCase
from app.api.task_activity.use_cases import ActivityUseCase

from app.lib.storage_util import StorageUtil

from app.api.exceptions.task_exceptions import TaskNotFoundException

from app.api.exceptions.task_attachment_exceptions import (
    InvalidFileTypeException,
    ImageTooLargeException,
    PDFTooLargeException,
    VideoTooLargeException,
)

ALLOWED_MIME_TYPES = {
    "image/jpeg": ("image", 10 * 1024 * 1024),
    "image/png": ("image", 10 * 1024 * 1024),
    "image/webp": ("image", 10 * 1024 * 1024),
    "application/pdf": ("pdf", 50 * 1024 * 1024),
    "video/mp4": ("video", 1000 * 1024 * 1024),
}

class TaskAttachmentUseCase:

    def __init__(self, session: AsyncSession):

        self.repository = TaskAttachmentRepository(session)
        self.task_repo = TaskRepository(session)

        self.storage_util = StorageUtil()

        self.notification_use_case = NotificationUseCase(
            NotificationRepository(session)
        )

        self.activity_use_case = ActivityUseCase(session)

    async def upload_file(
        self,
        task_id: uuid.UUID,
        file: UploadFile,
        current_user,
    ):

        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()


        file_info = ALLOWED_MIME_TYPES.get(
            file.content_type
        )

        if not file_info:
            raise InvalidFileTypeException()

        file_type, max_size = file_info

        file_size = getattr(file, "size", None)

        if file_size is None:
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)

        if file_size > max_size:

            if file_type == "image":
                raise ImageTooLargeException()

            elif file_type == "pdf":
                raise PDFTooLargeException()

            elif file_type == "video":
                raise VideoTooLargeException()

        filename = file.filename or "unknown_file"

        extension = (
            filename.split(".")[-1]
            if "." in filename
            else "bin"
        )

        path = (
            f"tasks/{task_id}/"
            f"{uuid.uuid4()}.{extension}"
        )

        file_url = self.storage_util.upload_file(
            file,
            path
        )

        attachment = await self.repository.create(
            TaskAttachmentCreate(
                task_id=task_id,
                type=file_type,
                file_name=filename,
                file_url=file_url,
            )
        )

        await self.activity_use_case.create(
            board_id=task.column.board_id,
            user_id=current_user.id,
            task_id=task.id,
            action="attachment_added",
            description=(
                f'{current_user.full_name} attached file '
                f'"{filename}" to task "{task.title}"'
            ),
            details={
                "attachment_id": str(attachment.id),
                "attachment_type": file_type,
                "file_name": filename,
                "file_url": file_url,
            },
        )

        await self._notify_attachment(
            task,
            filename
        )


        return attachment

    async def add_link(
        self,
        task_id: uuid.UUID,
        title: str | None,
        url: str,
        current_user,
    ):

        task = await self.task_repo.get_by_id(
            task_id
        )

        if not task:
            raise TaskNotFoundException()

        attachment = await self.repository.create(
            TaskAttachmentCreate(
                task_id=task_id,
                type="link",
                file_name=(
                    title
                    if title and title.strip()
                    else url
                ),
                file_url=url,
            )
        )

        await self.activity_use_case.create(
            board_id=task.column.board_id,
            user_id=current_user.id,
            task_id=task.id,
            action="attachment_added",
            description=(
                f'{current_user.full_name} attached link '
                f'"{attachment.file_name}" to task "{task.title}"'
            ),
            details={
                "attachment_id": str(attachment.id),
                "attachment_type": "link",
                "title": attachment.file_name,
                "url": url,
            },
        )

        await self._notify_attachment(
            task,
            attachment.file_name
        )

        return attachment

    async def _notify_attachment(
        self,
        task,
        filename: str,
    ):

        for user_id in task.assignee_ids or []:

            await self.notification_use_case.create(
                user_id=user_id,
                board_id=task.column.board_id,
                task_id=task.id,
                type="attachment_added",
                title="Attachment Added",
                message=(
                    f'Attachment "{filename}" '
                    f'was added to task "{task.title}".'
                ),
            )

    def generate_signed_url(
        self,
        file_url: str
    ) -> str:

        return self.storage_util.generate_signed_url(
            file_url
        )

    async def delete_attachment(
        self,
        attachment_id: uuid.UUID,
        current_user,
    ):

        attachment = await self.repository.get_by_id(
            attachment_id
        )

        if not attachment:
            return None

        task = await self.task_repo.get_by_id(
            attachment.task_id
        )

        if not task:
            raise TaskNotFoundException()

        if attachment.type != "link":
            self.storage_util.delete_file(
                attachment.file_url
            )

        await self.repository.delete(
            attachment_id
        )

        await self.activity_use_case.create(
            board_id=task.column.board_id,
            user_id=current_user.id,
            task_id=task.id,
            action="attachment_deleted",
            description=(
                f'{current_user.full_name} deleted attachment '
                f'"{attachment.file_name}" from task "{task.title}"'
            ),
            details={
                "attachment_id": str(attachment.id),
                "attachment_type": attachment.type,
                "file_name": attachment.file_name,
                "file_url": attachment.file_url,
            },
        )

        return attachment