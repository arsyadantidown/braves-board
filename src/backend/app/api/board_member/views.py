import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.standard_response import success_response

from app.models.user_model import User

from app.api.board_member.repository import BoardMemberRepository
from app.api.board_member.use_cases import BoardMemberUseCase
from app.api.board_member.schema import (
    BoardMemberCreate,
    BoardMemberUpdate,
)

from app.core.dependencies import require_permission


router = APIRouter(
    prefix="/api/v1/boards/{board_id}/members",
    tags=["Board Members"],
)


def get_board_member_use_case(
    db: AsyncSession = Depends(get_db),
) -> BoardMemberUseCase:
    repo = BoardMemberRepository(db)
    return BoardMemberUseCase(repo)


@router.get("", status_code=status.HTTP_200_OK)
async def get_board_members(
    board_id: uuid.UUID,
    use_case: BoardMemberUseCase = Depends(get_board_member_use_case),
    current_user: User = Depends(
        require_permission("member.view")
    ),
):
    result = await use_case.get_all(board_id)
    return success_response(result)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_board_member(
    board_id: uuid.UUID,
    member_in: BoardMemberCreate,
    use_case: BoardMemberUseCase = Depends(get_board_member_use_case),
    current_user: User = Depends(
        require_permission("member.invite")
    ),
):
    result = await use_case.create(
        board_id,
        member_in,
    )

    return success_response(result)


@router.patch("/{user_id}", status_code=status.HTTP_200_OK)
async def update_board_member(
    board_id: uuid.UUID,
    user_id: uuid.UUID,
    member_in: BoardMemberUpdate,
    use_case: BoardMemberUseCase = Depends(get_board_member_use_case),
    current_user: User = Depends(
        require_permission("member.change_role")
    ),
):
    result = await use_case.update(
        board_id,
        user_id,
        member_in,
    )

    return success_response(result)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_board_member(
    board_id: uuid.UUID,
    user_id: uuid.UUID,
    use_case: BoardMemberUseCase = Depends(get_board_member_use_case),
    current_user: User = Depends(
        require_permission("member.remove")
    ),
):
    await use_case.delete(
        board_id,
        user_id,
    )

    return success_response(None)