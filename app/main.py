"""FastAPI 애플리케이션 메인 파일"""
import logging
import sys
import os
from fastapi import FastAPI
from utils.logs.formatter import ColoredFormatter
from utils.logs.ascii_art import print_startup_banner
from utils.logs.logger import log_error

# 배너는 한 번만 출력 (reload 시 중복 출력 방지)
if not os.environ.get("UVICORN_RELOAD"):
    print_startup_banner()

# 로깅 설정
if not logging.getLogger().handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter('%(levelname)s:     %(message)s'))
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=False
    )

logger = logging.getLogger(__name__)

# settings 초기화
try:
    from config import settings  # import 시 자동으로 초기화 및 검증됨
    
    # settings 로드 후 로깅 레벨 조정
    logging.getLogger().setLevel(logging.DEBUG if settings.debug else logging.INFO)
except Exception as e:
    log_error("Settings validation failed", e)
    raise

# service import
try:
    from services import *
except Exception as e:
    log_error("Service initialization failed", e)
    raise

# controller import
try:
    from routes import *
except Exception as e:
    log_error("Controller/Router loading failed", e)
    raise

# middleware import
try:
    from middleware import *
except Exception as e:
    log_error("Middleware loading failed", e)
    raise


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    app = FastAPI(
        title="FastAPI REST API",
        description="MVC 패턴으로 구성된 FastAPI REST API 서버 (WebSocket 지원)",
        version="0.1.0"
    )
    
    # 미들웨어 추가
    if settings.debug:
        app.add_middleware(LoggingMiddleware)
    
    # CORS 미들웨어 추가
    setup_cors(app)
    
    # REST API 라우터 등록
    app.include_router(api_router, prefix="/api/v1")
    
    # WebSocket 라우터 등록
    app.include_router(websocket_router)
    
    # Exception Handler
    setup_error_handlers(app)
    
    @app.get("/")
    async def root():
        """루트 엔드포인트"""
        return {
            "message": "FastAPI REST API 서버입니다.",
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    return app

# 애플리케이션 인스턴스 싱글톤 패턴
_app_instance: FastAPI | None = None

def get_app() -> FastAPI:
    """애플리케이션 인스턴스를 반환하는 함수 (싱글톤 패턴)"""
    global _app_instance
    if _app_instance is None:
        _app_instance = create_app()
    return _app_instance


# 모듈 레벨에서 app 인스턴스 생성 (uvicorn이 "app.main:app"으로 참조)
app = get_app()

if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    # reload 모드 설정 (개발 환경에서만)
    reload_enabled = settings.debug if hasattr(settings, 'debug') else True
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.server_port,
        reload=reload_enabled,
        reload_dirs=["app", "controllers", "services", "middleware", "routes"] if reload_enabled else None
    )
