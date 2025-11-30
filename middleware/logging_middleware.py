"""로깅 미들웨어"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """요청 처리 전후 로깅"""
        start_time = time.time()
        
        # 요청 로깅
        logger.info(
            f"요청: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        try:
            response = await call_next(request)
            
            # 응답 로깅
            process_time = time.time() - start_time
            logger.info(
                f"응답: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
            
            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"오류: {request.method} {request.url.path} - "
                f"Error: {str(e)} - "
                f"Time: {process_time:.4f}s"
            )
            raise

