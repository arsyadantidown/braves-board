from fastapi import status

from app.api.exceptions.base_exceptions import CustomException


class NotificationNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Notification tidak ditemukan",
        )