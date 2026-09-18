import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.board.repository import BoardRepository
from app.api.board.use_cases import BoardUseCase
from app.api.board.schema import BoardCreate, BoardUpdate
from app.api.depedencies import get_current_user
from app.core.dependencies import require_permission
from app.models.user_model import User
from app.api.standard_response import success_response


router = APIRouter(prefix="/api/v1/boards", tags=["Boards"])

def get_board_use_case(db: AsyncSession = Depends(get_db)) -> BoardUseCase:
    repo = BoardRepository(db)
    return BoardUseCase(repo, db)

@router.get("", status_code=status.HTTP_200_OK)
async def get_boards(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case: BoardUseCase = Depends(get_board_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.get_all(current_user.id, limit, offset)
    return success_response(result)

@router.get("/{board_id}", status_code=status.HTTP_200_OK)
async def get_board_detail(
    board_id: uuid.UUID,
    use_case: BoardUseCase = Depends(get_board_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.get_detail(board_id, current_user.id)
    return success_response(result)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_board(
    board_in: BoardCreate,
    use_case: BoardUseCase = Depends(get_board_use_case),
    current_user: User = Depends(get_current_user),
):
    result = await use_case.create(board_in, current_user.id)
    return success_response(result)

@router.patch("/{board_id}", status_code=status.HTTP_200_OK)
async def update_board(
    board_id: uuid.UUID,
    update_data: BoardUpdate,
    use_case: BoardUseCase = Depends(get_board_use_case),
    current_user: User = Depends(
        require_permission("board.update")
    ),
):
    result = await use_case.update(
        board_id,
        update_data.model_dump(exclude_unset=True),
        current_user.id,
    )

    return success_response(result)

@router.delete("/{board_id}", status_code=status.HTTP_200_OK)
async def delete_board(
    board_id: uuid.UUID,
    use_case: BoardUseCase = Depends(get_board_use_case),
    current_user: User = Depends(
        require_permission("board.delete")
    ),
):
    await use_case.delete(board_id, current_user.id)
    return success_response(None)