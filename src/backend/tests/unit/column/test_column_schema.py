import uuid
import pytest
from pydantic import ValidationError

from app.api.column.schema import ColumnCreate,ColumnUpdate


def test_column_create_empty_title_should_fail():

    with pytest.raises(ValidationError):

        ColumnCreate(
            title="",
            board_id=uuid.uuid4()
        )


def test_column_create_whitespace_title_should_fail():

    with pytest.raises(ValidationError):

        ColumnCreate(
            title="   ",
            board_id=uuid.uuid4()
        )


def test_column_create_valid_title():

    column = ColumnCreate(
        title="Todo",
        board_id=uuid.uuid4()
    )

    assert column.title == "Todo"

def test_column_update_empty_title_should_fail():

    with pytest.raises(ValidationError):

        ColumnUpdate(
            title=""
        )


def test_column_update_whitespace_title_should_fail():

    with pytest.raises(ValidationError):

        ColumnUpdate(
            title="   "
        )


def test_column_update_valid_title():

    column = ColumnUpdate(
        title="In Progress"
    )

    assert column.title == "In Progress"