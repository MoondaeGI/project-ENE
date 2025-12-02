"""에러 처리 미들웨어"""
import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from exceptions import BaseAPIException

logger = logging.getLogger(__name__)


class ErrorMiddleware:
    """에러를 중앙에서 처리하는 미들웨어"""
    
    @staticmethod
    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """모든 예외를 처리하는 핸들러"""
        
        # 커스텀 API 예외 처리
        if isinstance(exc, BaseAPIException):
            logger.warning(
                f"[{exc.error_code}] {exc.message} - "
                f"Path: {request.url.path}, Method: {request.method}"
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.error_code,
                        "message": exc.message,
                        "detail": exc.detail
                    }
                }
            )
        
        # FastAPI의 HTTPException 처리
        if isinstance(exc, StarletteHTTPException):
            logger.warning(
                f"[HTTPException] {exc.detail} - "
                f"Path: {request.url.path}, Method: {request.method}"
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": "HTTP_EXCEPTION",
                        "message": exc.detail,
                        "detail": exc.detail
                    }
                }
            )
        
        # Pydantic 검증 에러 처리
        if isinstance(exc, RequestValidationError):
            errors = exc.errors()
            logger.warning(
                f"[ValidationError] 요청 검증 실패 - "
                f"Path: {request.url.path}, Method: {request.method}, "
                f"Errors: {errors}"
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "요청 데이터 검증에 실패했습니다.",
                        "detail": errors
                    }
                }
            )
        
        # 알 수 없는 예외 처리
        logger.error(
            f"[UnhandledException] 예상치 못한 에러 발생 - "
            f"Path: {request.url.path}, Method: {request.method}",
            exc_info=True
        )
        
        # 개발 환경에서는 상세한 에러 정보 제공
        from config import settings
        error_detail = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "내부 서버 오류가 발생했습니다.",
            }
        }
        
        if settings.debug:
            error_detail["error"]["detail"] = {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc().split("\n")
            }
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_detail
        )


def setup_error_handlers(app):
    """FastAPI 앱에 에러 핸들러 등록"""
    app.add_exception_handler(BaseAPIException, ErrorMiddleware.exception_handler)
    app.add_exception_handler(StarletteHTTPException, ErrorMiddleware.exception_handler)
    app.add_exception_handler(RequestValidationError, ErrorMiddleware.exception_handler)
    app.add_exception_handler(Exception, ErrorMiddleware.exception_handler)

