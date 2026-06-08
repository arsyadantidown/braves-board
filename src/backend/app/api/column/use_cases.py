import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.column.schema import ColumnCreate
from app.api.column.repository import ColumnRepository
from app.api.board.repository import BoardRepository
from app.api.exceptions.column_exceptions import (
    ColumnNotFoundException,
    InvalidColumnPositionException,
)
from app.api.exceptions.board_exceptions import BoardNotFoundException

class ColumnUseCase:
    def __init__(self, session: AsyncSession):
        self.repo = ColumnRepository(session)
        self.board_repo = BoardRepository(session)

    def _column_to_dict(self, column):
        return {
            "id": str(column.id),
            "board_id": str(column.board_id),
            "title": column.title,
            "position": column.position,
            "created_at": column.created_at,
            "updated_at": column.updated_at,
        }

    async def get_by_id(self, column_id: uuid.UUID):
        column = await self.repo.get_by_id(column_id)
        if not column:
            raise ColumnNotFoundException()
        return self._column_to_dict(column)

    async def get_all_by_board_id(
        self,
        board_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        board = await self.board_repo.get_by_id(board_id, user_id)

        if not board:
            raise BoardNotFoundException()

        columns = await self.repo.get_all_by_board_id(board_id)
        return [self._column_to_dict(c) for c in columns]

    async def create_column(self, column_in: ColumnCreate):
        column = await self.repo.create(column_in)
        return self._column_to_dict(column)

    async def update_column(self, column_id: uuid.UUID, update_data: dict):
        column = await self.repo.update(column_id, update_data)
        if not column:
            raise ColumnNotFoundException()
        return self._column_to_dict(column)

    async def delete_column(self, column_id: uuid.UUID):
        success = await self.repo.soft_delete(column_id)
        if not success:
            raise ColumnNotFoundException()
        return None

    async def reorder_column(self, column_id: uuid.UUID, new_position: int):
        column = await self.repo.reorder(column_id, new_position)
        if not column:
            raise InvalidColumnPositionException()
        return self._column_to_dict(column)
