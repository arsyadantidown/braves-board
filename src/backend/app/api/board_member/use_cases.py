import uuid

from app.api.board_member.repository import BoardMemberRepository
from app.api.board_member.schema import (
    BoardMemberCreate,
    BoardMemberUpdate,
    BoardMemberResponse,
)
from app.api.user.repository import UserRepository
from app.api.exceptions.board_exceptions import BoardNotFoundException


class BoardMemberUseCase:
    def __init__(
        self,
        repo: BoardMemberRepository,
        user_repo: UserRepository,
    ):
        self.repo = repo
        self.user_repo = user_repo

    async def get_all(self, board_id: uuid.UUID):
        members = await self.repo.get_all(board_id)

        return [
            BoardMemberResponse.model_validate(member).model_dump(mode="json")
            for member in members
        ]

    async def get_available_members(self, board_id: uuid.UUID):
        users = await self.user_repo.get_available_members(board_id)

        return [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "picture_url": user.picture_url,
            }
            for user in users
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

        if not member:
            raise BoardNotFoundException()

        return BoardMemberResponse.model_validate(
            member
        ).model_dump(mode="json")

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
            raise BoardNotFoundException()

        return BoardMemberResponse.model_validate(
            member
        ).model_dump(mode="json")

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
            raise BoardNotFoundException()

        return {
            "message": "Member deleted successfully"
        }