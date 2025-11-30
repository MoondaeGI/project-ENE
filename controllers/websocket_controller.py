"""WebSocket 컨트롤러"""
import logging
from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from services.websocket_service import websocket_service
from services.llm_service import llm_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 엔드포인트"""
    # 연결 시도 로그 (print로 즉시 출력)
    origin = websocket.headers.get("origin", "없음")
    client_host = websocket.client.host if websocket.client else "Unknown"
    path = websocket.url.path
    
    try:
        await websocket_service.connect(websocket)
        logger.info(f"[WebSocket] 연결 성공 - Origin: {origin}, Client: {client_host}")
    except Exception as e:
        logger.error(f"[WebSocket] 연결 실패 - Origin: {origin}, Client: {client_host}, Error: {str(e)}")
        logger.exception(e)  # 전체 스택 트레이스
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
            logger.info(f"[WebSocket] 사용자 메시지 수신: {user_message[:50]}...")
            
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
            
    except WebSocketDisconnect:
        websocket_service.disconnect(websocket)
        logger.info(f"[WebSocket] 클라이언트 연결이 끊어졌습니다. 현재 연결 수: {websocket_service.get_connection_count()}")
    except Exception as e:
        logger.error(f"[WebSocket] 오류 발생: {str(e)}")
        logger.exception(e)
        websocket_service.disconnect(websocket)


@router.websocket("/ws/{client_id}")
async def websocket_with_id(websocket: WebSocket, client_id: str):
    """클라이언트 ID를 받는 WebSocket 엔드포인트"""
    origin = websocket.headers.get("origin", "없음")
    client_host = websocket.client.host if websocket.client else "Unknown"
    
    logger.info(f"[WebSocket] 연결 시도 (ID: {client_id}) - Origin: {origin}, Client: {client_host}")
    
    try:
        await websocket_service.connect(websocket)
        logger.info(f"[WebSocket] 연결 성공 (ID: {client_id})")
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
            response = f"[{client_id}] 서버 응답: {data}"
            await websocket_service.send_personal_message(response, websocket)
            
    except WebSocketDisconnect:
        websocket_service.disconnect(websocket)
        logger.info(f"[WebSocket] 클라이언트 {client_id} 연결이 끊어졌습니다.")
    except Exception as e:
        logger.error(f"[WebSocket] 오류 발생 (ID: {client_id}): {str(e)}")
        logger.exception(e)
        websocket_service.disconnect(websocket)

