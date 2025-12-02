"""컨트롤러 패키지"""
from controllers.person_controller import router as person_router
from controllers.websocket_controller import router as websocket_router

__all__ = [
    "person_router",
    "websocket_router", 
]
