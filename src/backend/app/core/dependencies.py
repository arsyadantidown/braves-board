import uuid

from fastapi import Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.postgres import get_db
from app.api.depedencies import get_current_user

from app.models.user_model import User

from app.api.board_member.repository import BoardMemberRepository

from app.core.permission import has_permission


def require_permission(permission: str):

    async def checker(
        board_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):

        repo = BoardMemberRepository(db)

        role = await repo.get_role(
            board_id=board_id,
            user_id=current_user.id,
        )


        if role is None:
            raise HTTPException(
                status_code=403,
                detail="Not a board member"
            )


        if not has_permission(
            role,
            permission,
        ):
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )


        return current_user

    return checker