import uuid

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.models.user_model import User

from app.api.task_attachment.schema import (
    TaskAttachmentResponse,
    AddLinkRequest,
)
from app.api.task_attachment.use_cases import TaskAttachmentUseCase
from app.api.exceptions.task_attachment_exceptions import AttachmentNotFoundException
from app.api.standard_response import success_response

from app.core.dependencies import require_permission


router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["Task Attachments"]
)


def get_task_attachment_use_case(
    db: AsyncSession = Depends(get_db)
) -> TaskAttachmentUseCase:
    return TaskAttachmentUseCase(db)


@router.post(
    "/{task_id}/attachments/file",
    status_code=status.HTTP_201_CREATED
)
async def upload_task_attachment(
    task_id: uuid.UUID,
    file: UploadFile = File(...),
    use_case: TaskAttachmentUseCase = Depends(
        get_task_attachment_use_case
    ),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    attachment = await use_case.upload_file(
        task_id,
        file
    )

    attachment_dict = (
        TaskAttachmentResponse
        .model_validate(attachment)
        .model_dump(mode="json")
    )

    attachment_dict["file_url"] = (
        use_case.generate_signed_url(
            attachment.file_url
        )
    )

    return success_response(attachment_dict)


@router.post(
    "/{task_id}/attachments/link",
    status_code=status.HTTP_201_CREATED
)
async def add_task_attachment_link(
    task_id: uuid.UUID,
    request: AddLinkRequest,
    use_case: TaskAttachmentUseCase = Depends(
        get_task_attachment_use_case
    ),
    current_user: User = Depends(
        require_permission("task.update")
    ),
):
    attachment = await use_case.add_link(
        task_id=task_id,
        title=request.title,
        url=str(request.url),
    )

    attachment_dict = (
        TaskAttachmentResponse
        .model_validate(attachment)
        .model_dump(mode="json")
    )

    return success_response(attachment_dict)


@router.delete(
    "/attachments/{id}",
    status_code=status.HTTP_200_OK
)
async def delete_attachment(
    id: uuid.UUID,
    use_case: TaskAttachmentUseCase = Depends(
        get_task_attachment_use_case
    ),
    current_user: User = Depends(
        require_permission("task.delete")
    ),
):
    attachment = await use_case.delete_attachment(
        id
    )

    if not attachment:
        raise AttachmentNotFoundException()

    return success_response(
        {"message": "Lampiran berhasil dihapus"}
    )