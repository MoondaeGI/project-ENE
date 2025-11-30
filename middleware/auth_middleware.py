"""인증 미들웨어 (추후 확장용)"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class AuthMiddleware(BaseHTTPMiddleware):
    """인증 미들웨어 - 추후 JWT 토큰 검증 등에 사용"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """요청 처리 전 인증 검증"""
        
        # 공개 경로는 인증 검증 제외
        public_paths = ["/", "/docs", "/openapi.json", "/redoc", "/api/v1/health"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        # WebSocket은 별도 처리
        if request.url.path.startswith("/ws"):
            return await call_next(request)
        
        # TODO: JWT 토큰 검증 로직 추가
        # authorization = request.headers.get("Authorization")
        # if not authorization or not self.verify_token(authorization):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="인증이 필요합니다."
        #     )
        
        return await call_next(request)

