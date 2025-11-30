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
        
        # WebSocket 업그레이드 요청 체크
        is_websocket = request.headers.get("upgrade", "").lower() == "websocket"
        origin = request.headers.get("origin", "없음")
        
        # 요청 로깅
        log_msg = (
            f"요청: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        if is_websocket:
            log_msg += f" - [WebSocket] Origin: {origin}"
            print(f"[로깅 미들웨어] {log_msg}")
            logger.info(log_msg)
            print(f"[로깅 미들웨어] [WebSocket 업그레이드 요청] 전체 헤더: {dict(request.headers)}")
            logger.debug(f"[WebSocket 업그레이드 요청] 전체 헤더: {dict(request.headers)}")
        else:
            logger.info(log_msg)
        
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

