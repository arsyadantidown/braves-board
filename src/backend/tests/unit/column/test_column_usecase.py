import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.api.column.use_cases import ColumnUseCase
from app.api.exceptions.board_exceptions import BoardNotFoundException
from app.api.exceptions.column_exceptions import ColumnNotFoundException

@pytest.mark.anyio
async def test_get_columns_invalid_board_should_raise():

    use_case = ColumnUseCase(MagicMock())

    use_case.board_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(BoardNotFoundException):

        await use_case.get_all_by_board_id(
            uuid.uuid4(),
            uuid.uuid4()
        )

@pytest.mark.anyio
async def test_get_column_by_id_not_found():

    use_case = ColumnUseCase(MagicMock())

    use_case.repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(ColumnNotFoundException):

        await use_case.get_by_id(uuid.uuid4())