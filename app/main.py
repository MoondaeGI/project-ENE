"""FastAPI 애플리케이션 메인 파일"""
from fastapi import FastAPI
from routes import api_router
from controllers.websocket_controller import router as websocket_router


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    app = FastAPI(
        title="FastAPI REST API",
        description="MVC 패턴으로 구성된 FastAPI REST API 서버 (WebSocket 지원)",
        version="0.1.0"
    )
    
    # REST API 라우터 등록
    app.include_router(api_router, prefix="/api/v1")
    
    # WebSocket 라우터 등록
    app.include_router(websocket_router)
    
    @app.get("/")
    async def root():
        """루트 엔드포인트"""
        return {
            "message": "FastAPI REST API 서버입니다.",
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    return app


# 애플리케이션 인스턴스 생성
app = create_app()

if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.server_port,
        reload=True
    )

