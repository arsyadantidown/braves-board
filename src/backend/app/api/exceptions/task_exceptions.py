from fastapi import status
from app.api.exceptions.base_exceptions import CustomException

class InvalidAssigneeException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Satu atau lebih assignee tidak valid atau tidak ditemukan"
        )

class ColumnNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Kolom tidak ditemukan",
        )

class TaskNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Task tidak ditemukan",
        )

class InvalidTargetColumnException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Kolom target tidak valid",
        )

class InvalidTaskPositionException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Posisi task tidak valid",
        )

class InvalidUUIDFormatException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Format ID tidak valid. Harap gunakan format UUID yang benar.",
        )