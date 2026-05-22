from fastapi import status
from app.api.exceptions.base_exceptions import CustomException

class InvalidCredentialsException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Kredensial tidak valid",
        )

class TokenExpiredException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Token telah kedaluwarsa",
        )

class InvalidTokenException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Token tidak valid atau telah kedaluwarsa",
        )

class MissingTokenException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Token autentikasi tidak ditemukan",
        )

class MissingUserAgentException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message="User-Agent header wajib disertakan",
        )

class GoogleAuthException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Gagal menghasilkan URL autentikasi Google",
        )

class InvalidGoogleCodeException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Kode autentikasi Google tidak valid",
        )

class ForbiddenDomainException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Akses ditolak. Akses hanya untuk akun resmi perusahaan.",
        )

class InvalidRefreshTokenException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Refresh token tidak valid atau telah kedaluwarsa",
        )

class MissingRefreshTokenException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Refresh token tidak ditemukan",
        )

class SessionNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Sesi tidak ditemukan",
        )

class LogoutSuccessMessage:
    MESSAGE = "Berhasil keluar dari sistem"