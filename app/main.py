"""FastAPI 애플리케이션 메인 파일"""
import logging
import sys
from fastapi import FastAPI
from utils.logs.formatter import ColoredFormatter
from utils.logs.ascii_art import print_startup_banner

# 서버 시작 배너 출력
print_startup_banner()

# 1단계: 로깅 설정 먼저 (FastAPI/uvicorn 기본 형식 유지 + 색상)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ColoredFormatter('%(levelname)s:     %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

logger = logging.getLogger(__name__)

# 2단계: Settings를 가장 먼저 로드하고 검증
try:
    logger.info("Loading settings...")
    from config import validate_settings, settings
    
    # Settings 검증 (이 시점에 .env 파일을 읽고 모든 설정이 준비됨)
    validate_settings()
    logger.info(f"✓ Settings validated - App: {settings.app_name}, Port: {settings.server_port}, Debug: {settings.debug}")
    
    # settings 로드 후 로깅 레벨 조정
    logging.getLogger().setLevel(logging.DEBUG if settings.debug else logging.INFO)
except Exception as e:
    logger.error(f"✗ Settings validation failed: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise

# 3단계: Services 초기화 검증
try:
    logger.info("Initializing services...")
    
    # LLM Service 초기화 검증
    from services.llm_service import llm_service
    if llm_service.client:
        logger.info("✓ LLM Service initialized")
    else:
        logger.warning("⚠ LLM Service initialized (API key not set)")
    
    # WebSocket Service 초기화 검증
    from services.websocket_service import websocket_service
    logger.info("✓ WebSocket Service initialized")
    
    # Health Service 초기화 검증
    from services.health_service import HealthService
    logger.info("✓ Health Service initialized")
    
    # User Service 초기화 검증
    from services.user_service import UserService
    logger.info("✓ User Service initialized")
    
except Exception as e:
    logger.error(f"✗ Service initialization failed: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise

# 4단계: Controllers 및 Routes 초기화 검증
try:
    logger.info("Loading controllers and routes...")
    
    from routes import api_router
    from controllers.websocket_controller import router as websocket_router
    from controllers.health_controller import router as health_router
    from controllers.user_controller import router as user_router
    
    logger.info("✓ Health Controller loaded")
    logger.info("✓ User Controller loaded")
    logger.info("✓ WebSocket Controller loaded")
    logger.info("✓ API Router configured")
    
except Exception as e:
    logger.error(f"✗ Controller/Router loading failed: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise

# 5단계: Middleware 초기화 검증
try:
    logger.info("Loading middleware...")
    
    from middleware.cors_middleware import setup_cors
    from middleware.logging_middleware import LoggingMiddleware
    
    logger.info("✓ CORS Middleware loaded")
    if settings.debug:
        logger.info("✓ Logging Middleware loaded (debug mode)")
    
except Exception as e:
    logger.error(f"✗ Middleware loading failed: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    logger.info("Creating FastAPI application...")
    
    app = FastAPI(
        title="FastAPI REST API",
        description="MVC 패턴으로 구성된 FastAPI REST API 서버 (WebSocket 지원)",
        version="0.1.0"
    )
    
    # 미들웨어 등록 (라우터 등록 전에! 순서 중요)
    logger.info("Registering middleware...")
    
    # 1. 로깅 미들웨어 (가장 먼저 실행되어야 함)
    if settings.debug:
        app.add_middleware(LoggingMiddleware)
        logger.info("✓ Logging Middleware registered")
    
    # 2. CORS 미들웨어
    setup_cors(app)
    logger.info("✓ CORS Middleware registered")
    
    # 3. 인증 미들웨어는 필요 시 추가
    # from middleware.auth_middleware import AuthMiddleware
    # app.add_middleware(AuthMiddleware)
    
    # REST API 라우터 등록
    logger.info("Registering routes...")
    app.include_router(api_router, prefix="/api/v1")
    logger.info("✓ API Router registered at /api/v1")
    
    # WebSocket 라우터 등록
    app.include_router(websocket_router)
    logger.info("✓ WebSocket Router registered at /ws")
    
    @app.get("/")
    async def root():
        """루트 엔드포인트"""
        return {
            "message": "FastAPI REST API 서버입니다.",
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    logger.info("✓ FastAPI application created successfully")
    return app

# reload 모드에서도 안전하게 작동하도록 싱글톤 패턴 사용
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
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.server_port,
        reload=True
    )

