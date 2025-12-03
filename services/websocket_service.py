import logging
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketService:
    
    def __init__(self):
        # 활성 연결 관리
        self.active_connections: Set[WebSocket] = set()
        # 클라이언트별 연결 관리 (추가 정보 저장 시 사용)
        self.client_connections: Dict[WebSocket, dict] = {}
        
    
    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            
            self.active_connections.add(websocket)
            self.client_connections[websocket] = {
                "connected_at": datetime.now()
            }
        except Exception as e:
            logger.error(f"[WebSocketService] 연결 수락 실패: {str(e)}")
            logger.exception(e)
            raise
    

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        self.client_connections.pop(websocket, None)

    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"[WebSocketService] 메시지 전송 오류: {e}")
            self.disconnect(websocket)

    
    async def echo_message(self, websocket: WebSocket, message: str):
        response = f"서버 응답: {message}"
        await self.send_personal_message(response, websocket)
    

    def get_connection_count(self) -> int:
        return len(self.active_connections)


# 싱글톤 인스턴스
websocket_service = WebSocketService()

