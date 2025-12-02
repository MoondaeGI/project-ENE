"""로깅 미들웨어"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging
from utils.logs.logger import log_api_request, log_api_response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware): 
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # WebSocket 업그레이드 요청 체크 (WebSocket은 별도 로거에서 처리)
        is_websocket = request.headers.get("upgrade", "").lower() == "websocket"
        
        # WebSocket이 아닌 경우에만 API 로깅
        if not is_websocket:
            # 요청 본문 읽기 (선택적)
            request_body = None
            try:
                if request.method in ["POST", "PUT", "PATCH"]:
                    body = await request.body()
                    if body:
                        import json
                        try:
                            request_body = json.loads(body.decode())
                        except:
                            request_body = body.decode()[:500]  # 너무 길면 잘라내기
            except:
                pass
            
            # 요청 헤더 (민감한 정보 제외)
            request_headers = dict(request.headers)
            # Authorization 헤더는 보안상 일부만 표시
            if "authorization" in request_headers:
                auth_value = request_headers["authorization"]
                if len(auth_value) > 20:
                    request_headers["authorization"] = auth_value[:20] + "..."
            
            # API 요청 로깅
            log_api_request(
                method=request.method,
                path=str(request.url.path),
                client_host=request.client.host if request.client else None,
                request_headers=request_headers,
                request_body=request_body
            )
        
        try:
            response = await call_next(request)
            
            # WebSocket이 아닌 경우에만 API 응답 로깅
            if not is_websocket:
                process_time = time.time() - start_time
                
                # 응답 본문 읽기 (선택적, 작은 응답만)
                response_body = None
                try:
                    # 응답 본문을 읽기 위해 스트림을 읽어야 하지만,
                    # 이미 읽은 경우 재사용할 수 없으므로 여기서는 생략
                    # 필요시 별도 미들웨어에서 처리
                    pass
                except:
                    pass
                
                # API 응답 로깅
                log_api_response(
                    method=request.method,
                    path=str(request.url.path),
                    status_code=response.status_code,
                    process_time=process_time,
                    client_host=request.client.host if request.client else None,
                    response_body=response_body
                )
                
                # 응답 헤더에 처리 시간 추가
                response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # WebSocket이 아닌 경우에만 에러 로깅
            if not is_websocket:
                log_api_response(
                    method=request.method,
                    path=str(request.url.path),
                    status_code=500,
                    process_time=process_time,
                    client_host=request.client.host if request.client else None,
                    error=str(e)
                )
            
            raise

