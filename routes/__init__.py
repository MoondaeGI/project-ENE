"""라우터 패키지"""
from fastapi import APIRouter
from controllers import person_router, websocket_router

# 메인 API 라우터
api_router = APIRouter()

# 각 컨트롤러 라우터 등록
api_router.include_router(user_router)

__all__ = [
    "api_router",
    "person_router",
    "websocket_router",
]
