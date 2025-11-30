"""WebSocket 컨트롤러"""
import logging
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from services.websocket_service import websocket_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 엔드포인트"""
    # 연결 시도 로그 (print로 즉시 출력)
    origin = websocket.headers.get("origin", "없음")
    client_host = websocket.client.host if websocket.client else "Unknown"
    path = websocket.url.path
    
    print(f"[WebSocket] ========== 연결 시도 ==========")
    print(f"[WebSocket] Path: {path}")
    print(f"[WebSocket] Origin: {origin}")
    print(f"[WebSocket] Client: {client_host}")
    print(f"[WebSocket] 전체 헤더: {dict(websocket.headers)}")
    
    logger.info(f"[WebSocket] 연결 시도 - Path: {path}, Origin: {origin}, Client: {client_host}")
    logger.debug(f"[WebSocket] 전체 헤더: {dict(websocket.headers)}")
    
    try:
        print(f"[WebSocket] 서비스 연결 시도...")
        await websocket_service.connect(websocket)
        print(f"[WebSocket] ✅ 연결 성공!")
        logger.info(f"[WebSocket] 연결 성공 - Origin: {origin}, Client: {client_host}")
    except Exception as e:
        print(f"[WebSocket] ❌ 연결 실패: {str(e)}")
        print(f"[WebSocket] 에러 타입: {type(e).__name__}")
        import traceback
        print(f"[WebSocket] 스택 트레이스:\n{traceback.format_exc()}")
        logger.error(f"[WebSocket] 연결 실패 - Origin: {origin}, Client: {client_host}, Error: {str(e)}")
        logger.exception(e)  # 전체 스택 트레이스
        raise
    
    try:
        # 연결 확인 메시지 전송
        await websocket_service.send_personal_message(
            "서버에 연결되었습니다!",
            websocket
        )
        
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            
            # 에코 응답
            await websocket_service.echo_message(websocket, data)
            
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

