import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.column.schema import ColumnCreate, ColumnUpdate
from app.api.column.use_cases import ColumnUseCase
from app.api.depedencies import get_current_user
from app.models.user_model import User
from app.api.standard_response import success_response


router = APIRouter(prefix="/api/v1/columns", tags=["Columns"])


def get_column_use_case(db: AsyncSession = Depends(get_db)) -> ColumnUseCase:
    return ColumnUseCase(db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_column(
    payload: ColumnCreate,
    use_case: ColumnUseCase = Depends(get_column_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.create_column(payload)
    return success_response(result)


@router.get("", status_code=status.HTTP_200_OK)
async def get_columns(
    board_id: uuid.UUID,
    use_case: ColumnUseCase = Depends(get_column_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.get_all_by_board_id(
        board_id,
        current_user.id,
    )
    return success_response(result)


@router.patch("/{column_id}", status_code=status.HTTP_200_OK)
async def update_column(
    column_id: uuid.UUID,
    payload: ColumnUpdate,
    use_case: ColumnUseCase = Depends(get_column_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.update_column(
        column_id,
        payload.model_dump(exclude_unset=True),
    )
    return success_response(result)


@router.delete("/{column_id}", status_code=status.HTTP_200_OK)
async def delete_column(
    column_id: uuid.UUID,
    use_case: ColumnUseCase = Depends(get_column_use_case),
    current_user: User = Depends(get_current_user),
):
    await use_case.delete_column(column_id)
    return success_response(None)


@router.patch("/{column_id}/reorder", status_code=status.HTTP_200_OK)
async def reorder_column(
    column_id: uuid.UUID,
    new_position: int,
    use_case: ColumnUseCase = Depends(get_column_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.reorder_column(column_id, new_position)
    return success_response(result)
