"""CORS 미들웨어"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings


def setup_cors(app: FastAPI) -> None:
    """CORS 미들웨어 설정"""
    # 개발 환경: 모든 Origin 허용
    # 프로덕션에서는 환경 변수로 관리
    allow_origins = ["*"]  # 개발용
    
    # 환경 변수에서 허용할 Origin 목록을 가져올 수 있음
    # allow_origins = settings.allowed_origins.split(",") if hasattr(settings, 'allowed_origins') else ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

