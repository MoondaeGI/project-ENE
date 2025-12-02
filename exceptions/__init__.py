"""커스텀 예외 클래스"""
from fastapi import status


class BaseAPIException(Exception):
    """API 예외의 기본 클래스"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str | None = None,
        error_code: str | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """유효성 검증 에러"""
    def __init__(self, message: str, detail: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class AuthenticationError(BaseAPIException):
    """인증 에러"""
    def __init__(self, message: str = "인증이 필요합니다.", detail: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(BaseAPIException):
    """권한 에러"""
    def __init__(self, message: str = "권한이 없습니다.", detail: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(BaseAPIException):
    """리소스를 찾을 수 없음"""
    def __init__(self, message: str = "리소스를 찾을 수 없습니다.", detail: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND_ERROR"
        )


class ConflictError(BaseAPIException):
    """충돌 에러 (예: 중복된 리소스)"""
    def __init__(self, message: str = "리소스가 이미 존재합니다.", detail: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT_ERROR"
        )


class InternalServerError(BaseAPIException):
    """내부 서버 에러"""
    def __init__(self, message: str = "내부 서버 오류가 발생했습니다.", detail: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="INTERNAL_SERVER_ERROR"
        )


class ServiceUnavailableError(BaseAPIException):
    """서비스 사용 불가 에러"""
    def __init__(self, message: str = "서비스를 사용할 수 없습니다.", detail: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="SERVICE_UNAVAILABLE_ERROR"
        )

