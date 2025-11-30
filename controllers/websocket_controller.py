"""WebSocket 컨트롤러"""
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from services.websocket_service import websocket_service

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 엔드포인트"""
    await websocket_service.connect(websocket)
    
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
        print(f"클라이언트 연결이 끊어졌습니다. 현재 연결 수: {websocket_service.get_connection_count()}")
    except Exception as e:
        print(f"WebSocket 오류: {e}")
        websocket_service.disconnect(websocket)


@router.websocket("/ws/{client_id}")
async def websocket_with_id(websocket: WebSocket, client_id: str):
    """클라이언트 ID를 받는 WebSocket 엔드포인트"""
    await websocket_service.connect(websocket)
    
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
        print(f"클라이언트 {client_id} 연결이 끊어졌습니다.")
    except Exception as e:
        print(f"WebSocket 오류: {e}")
        websocket_service.disconnect(websocket)

