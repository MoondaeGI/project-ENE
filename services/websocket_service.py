"""WebSocket 서비스"""
import logging
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketService:
    """WebSocket 연결 관리 및 비즈니스 로직"""
    
    def __init__(self):
        # 활성 연결 관리
        self.active_connections: Set[WebSocket] = set()
        # 클라이언트별 연결 관리 (추가 정보 저장 시 사용)
        self.client_connections: Dict[WebSocket, dict] = {}
        # 클라이언트별 대화 히스토리
        self.conversation_histories: Dict[WebSocket, list] = {}
    
    async def connect(self, websocket: WebSocket):
        """WebSocket 연결 수락"""
        try:
            await websocket.accept()
            
            self.active_connections.add(websocket)
            self.client_connections[websocket] = {
                "connected_at": datetime.now()
            }
            # 대화 히스토리 초기화
            self.conversation_histories[websocket] = []
        except Exception as e:
            logger.error(f"[WebSocketService] 연결 수락 실패: {str(e)}")
            logger.exception(e)
            raise
    
    def disconnect(self, websocket: WebSocket):
        """WebSocket 연결 해제"""
        self.active_connections.discard(websocket)
        self.client_connections.pop(websocket, None)
        # 대화 히스토리도 제거
        self.conversation_histories.pop(websocket, None)
    
    def get_conversation_history(self, websocket: WebSocket) -> list:
        """클라이언트의 대화 히스토리 가져오기"""
        return self.conversation_histories.get(websocket, [])
    
    def add_to_conversation_history(self, websocket: WebSocket, role: str, content: str):
        """대화 히스토리에 메시지 추가"""
        if websocket not in self.conversation_histories:
            self.conversation_histories[websocket] = []
        
        self.conversation_histories[websocket].append({
            "role": role,
            "content": content
        })
        
        # 히스토리 길이 제한 (최근 10턴만 유지)
        if len(self.conversation_histories[websocket]) > 20:  # 10턴 = 20개 메시지
            self.conversation_histories[websocket] = self.conversation_histories[websocket][-20:]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """특정 클라이언트에게 메시지 전송"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"[WebSocketService] 메시지 전송 오류: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """모든 연결된 클라이언트에게 브로드캐스트"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"[WebSocketService] 브로드캐스트 오류: {e}")
                disconnected.append(connection)
        
        # 연결이 끊어진 클라이언트 제거
        for connection in disconnected:
            self.disconnect(connection)
    
    async def echo_message(self, websocket: WebSocket, message: str):
        """에코 메시지 처리 (받은 메시지를 다시 전송)"""
        response = f"서버 응답: {message}"
        await self.send_personal_message(response, websocket)
    
    def get_connection_count(self) -> int:
        """현재 연결된 클라이언트 수 반환"""
        return len(self.active_connections)


# 싱글톤 인스턴스
websocket_service = WebSocketService()

