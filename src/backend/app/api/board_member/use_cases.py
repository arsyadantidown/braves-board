import uuid

from app.api.board_member.repository import BoardMemberRepository
from app.api.board_member.schema import (
    BoardMemberCreate,
    BoardMemberUpdate,
    BoardMemberResponse,
)

class BoardMemberUseCase:
    def __init__(self, repo: BoardMemberRepository):
        self.repo = repo

    async def get_all(self, board_id: uuid.UUID):
        members = await self.repo.get_all(board_id)

        return [
            BoardMemberResponse.model_validate(member).model_dump(mode="json")
            for member in members
        ]

    async def create(
        self,
        board_id: uuid.UUID,
        member_in: BoardMemberCreate,
    ):
        member = await self.repo.create(
            board_id=board_id,
            user_id=member_in.user_id,
            role=member_in.role,
        )

        return BoardMemberResponse.model_validate(member).model_dump(mode="json")

    async def update(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
        member_in: BoardMemberUpdate,
    ):
        member = await self.repo.update(
            board_id=board_id,
            user_id=user_id,
            role=member_in.role,
        )

        if not member:
            raise ValueError("Member not found")

        return BoardMemberResponse.model_validate(member).model_dump(mode="json")

    async def delete(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        deleted = await self.repo.soft_delete(
            board_id=board_id,
            user_id=user_id,
        )

        if not deleted:
            raise ValueError("Member not found")

        return True