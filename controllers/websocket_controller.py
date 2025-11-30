"""WebSocket 컨트롤러"""
import logging
import time
from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from services.websocket_service import websocket_service
from services.llm_service import llm_service
from utils.logs.logger import (
    log_websocket_connect,
    log_websocket_message,
    log_websocket_response,
    log_websocket_disconnect
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 엔드포인트"""
    origin = websocket.headers.get("origin", "없음")
    client_host = websocket.client.host if websocket.client else "Unknown"
    
    try:
        await websocket_service.connect(websocket)
        
        # WebSocket 연결 로깅
        log_websocket_connect(
            client_host=client_host,
            origin=origin,
            connection_count=websocket_service.get_connection_count()
        )
    except Exception as e:
        logger.error(f"[WebSocket] 연결 실패 - Origin: {origin}, Client: {client_host}, Error: {str(e)}")
        logger.exception(e)
        raise
    
    try:
        # 연결 확인 메시지 전송
        await websocket_service.send_personal_message(
            "서버에 연결되었습니다! 질문을 입력해주세요.",
            websocket
        )
        
        while True:
            # 클라이언트로부터 메시지 수신
            user_message = await websocket.receive_text()
            
            # 시간 측정 시작
            start_time = time.time()
            
            # WebSocket 메시지 수신 로깅
            log_websocket_message(
                message_content=user_message,
                client_host=client_host
            )
            
            # 대화 히스토리 가져오기
            conversation_history = websocket_service.get_conversation_history(websocket)
            
            # LLM 응답 생성
            await websocket_service.send_personal_message(
                "🤔 생각 중...",
                websocket
            )
            
            # LLM 서비스 사용 (다른 서비스들과 동일하게 직접 사용)
            if llm_service.client is None:
                llm_response = "⚠️ LLM 서비스가 초기화되지 않았습니다."
            else:
                llm_response = await llm_service.generate_response(
                    user_message=user_message,
                    conversation_history=conversation_history
                )
            
            # 대화 히스토리에 추가
            websocket_service.add_to_conversation_history(websocket, "user", user_message)
            websocket_service.add_to_conversation_history(websocket, "assistant", llm_response)
            
            # LLM 응답 전송
            await websocket_service.send_personal_message(llm_response, websocket)
            
            # 시간 측정 종료
            duration = time.time() - start_time
            
            # WebSocket 응답 전송 로깅
            log_websocket_response(
                response=llm_response,
                client_host=client_host,
                duration=duration
            )
            
    except WebSocketDisconnect:
        websocket_service.disconnect(websocket)
        
        # WebSocket 연결 해제 로깅
        log_websocket_disconnect(
            client_host=client_host,
            connection_count=websocket_service.get_connection_count()
        )
    except Exception as e:
        logger.error(f"[WebSocket] 오류 발생: {str(e)}")
        logger.exception(e)
        websocket_service.disconnect(websocket)
        
        # WebSocket 연결 해제 로깅
        log_websocket_disconnect(
            client_host=client_host,
            connection_count=websocket_service.get_connection_count()
        )


@router.websocket("/ws/{client_id}")
async def websocket_with_id(websocket: WebSocket, client_id: str):
    """클라이언트 ID를 받는 WebSocket 엔드포인트"""
    origin = websocket.headers.get("origin", "없음")
    client_host = websocket.client.host if websocket.client else "Unknown"
    
    try:
        await websocket_service.connect(websocket)
        
        # WebSocket 연결 로깅
        log_websocket_connect(
            client_host=client_host,
            origin=origin,
            connection_count=websocket_service.get_connection_count()
        )
    except Exception as e:
        logger.error(f"[WebSocket] 연결 실패 (ID: {client_id}) - Error: {str(e)}")
        logger.exception(e)
        raise
    
    try:
        await websocket_service.send_personal_message(
            f"서버에 연결되었습니다! (Client ID: {client_id})",
            websocket
        )
        
        while True:
            data = await websocket.receive_text()
            
            # 시간 측정 시작
            start_time = time.time()
            
            # WebSocket 메시지 수신 로깅
            log_websocket_message(
                message_content=data,
                client_host=client_host
            )
            
            response = f"[{client_id}] 서버 응답: {data}"
            await websocket_service.send_personal_message(response, websocket)
            
            # 시간 측정 종료
            duration = time.time() - start_time
            
            # WebSocket 응답 전송 로깅
            log_websocket_response(
                response=response,
                client_host=client_host,
                duration=duration
            )
            
    except WebSocketDisconnect:
        websocket_service.disconnect(websocket)
        
        # WebSocket 연결 해제 로깅
        log_websocket_disconnect(
            client_host=client_host,
            connection_count=websocket_service.get_connection_count()
        )
    except Exception as e:
        logger.error(f"[WebSocket] 오류 발생 (ID: {client_id}): {str(e)}")
        logger.exception(e)
        websocket_service.disconnect(websocket)
        
        # WebSocket 연결 해제 로깅
        log_websocket_disconnect(
            client_host=client_host,
            connection_count=websocket_service.get_connection_count()
        )

