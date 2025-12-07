"""WebSocket 컨트롤러"""
import logging
import time
from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from sqlalchemy.orm import Session
from config.database_config import get_db
from services import websocket_service, llm_service
from services.message_service import MessageService
from schemas.message import MessageCreate
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
            try:
                # 클라이언트로부터 메시지 수신
                user_message = await websocket.receive_text()
            except WebSocketDisconnect:
                # 연결이 정상적으로 끊어진 경우
                break
            except UnicodeDecodeError as e:
                logger.error(f"[WebSocket] 메시지 디코딩 실패 (UTF-8): {str(e)}")
                try:
                    await websocket_service.send_personal_message(
                        "⚠️ 메시지 인코딩 오류가 발생했습니다. UTF-8 형식의 텍스트만 지원합니다.",
                        websocket
                    )
                except:
                    # 메시지 전송 실패 시 연결이 끊어진 것으로 간주
                    break
                continue
            except Exception as e:
                # 연결이 끊어진 경우 (ConnectionClosedError 등)
                error_type = type(e).__name__
                if "ConnectionClosed" in error_type or "ConnectionError" in error_type:
                    break
                logger.error(f"[WebSocket] 메시지 수신 실패: {str(e)}")
                logger.exception(e)
                break  # 예상치 못한 오류는 루프 종료
            
            # 시간 측정 시작
            start_time = time.time()
            
            # WebSocket 메시지 수신 로깅
            try:
                log_websocket_message(
                    message_content=user_message,
                    client_host=client_host
                )
            except Exception as e:
                logger.error(f"[WebSocket] 메시지 로깅 실패: {str(e)}")
            
            # 메시지를 person_id 1번에 저장 (get_db()를 사용하여 자동 커밋/롤백)
            safe_content = user_message.encode('utf-8', errors='replace').decode('utf-8')
            message_data = MessageCreate(person_id=1, content=safe_content)
            
            # get_db()는 제너레이터이므로 for 루프로 사용하면 자동으로 commit/rollback 처리됨
            try:
                for db in get_db():
                    try:
                        MessageService.create_message(message_data, db)
                        logger.info(f"[WebSocket] 메시지 저장 완료 - person_id: 1")
                    except (UnicodeEncodeError, UnicodeDecodeError) as e:
                        # 인코딩 오류는 간단히 로깅 (에러 메시지 자체가 인코딩 문제를 일으킬 수 있음)
                        error_type = type(e).__name__
                        logger.error(f"[WebSocket] 메시지 저장 실패 ({error_type})")
                        raise  # get_db()의 except 블록에서 rollback 처리
                    except Exception as e:
                        # 에러 메시지를 안전하게 처리
                        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                        logger.error(f"[WebSocket] 메시지 저장 실패: {error_msg}")
                        raise  # get_db()의 except 블록에서 rollback 처리
                    break  # 한 번만 실행
            except Exception as e:
                # get_db() 외부에서 발생한 예외는 로깅만
                logger.error(f"[WebSocket] DB 세션 생성 실패: {str(e)}")  
            
            # LLM 응답 생성
            try:
                await websocket_service.send_personal_message(
                    "🤔 생각 중...",
                    websocket
                )
            except:
                # 메시지 전송 실패 시 연결이 끊어진 것으로 간주
                break
            
            # LLM 서비스 사용 (다른 서비스들과 동일하게 직접 사용)
            if llm_service.client is None:
                llm_response = "⚠️ LLM 서비스가 초기화되지 않았습니다."
            else:
                try:
                    llm_response = await llm_service.generate_response(user_message=user_message)
                except Exception as e:
                    logger.error(f"[WebSocket] LLM 응답 생성 실패: {str(e)}")
                    llm_response = "⚠️ 응답 생성 중 오류가 발생했습니다."
            
            # LLM 응답 전송
            try:
                await websocket_service.send_personal_message(llm_response, websocket)
            except:
                # 메시지 전송 실패 시 연결이 끊어진 것으로 간주
                break
            
            # 시간 측정 종료
            duration = time.time() - start_time
            
            # WebSocket 응답 전송 로깅
            log_websocket_response(
                response=llm_response,
                client_host=client_host,
                duration=duration
            )
            
    except WebSocketDisconnect:
        pass  # 이미 루프에서 처리됨
    except Exception as e:
        logger.error(f"[WebSocket] 오류 발생: {str(e)}")
        logger.exception(e)
    finally:
        # 항상 연결 정리
        try:
            websocket_service.disconnect(websocket)
            log_websocket_disconnect(
                client_host=client_host,
                connection_count=websocket_service.get_connection_count()
            )
        except Exception as e:
            logger.error(f"[WebSocket] 연결 정리 중 오류: {str(e)}")


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
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                # 연결이 정상적으로 끊어진 경우
                break
            except Exception as e:
                # 연결이 끊어진 경우 (ConnectionClosedError 등)
                error_type = type(e).__name__
                if "ConnectionClosed" in error_type or "ConnectionError" in error_type:
                    break
                logger.error(f"[WebSocket] 메시지 수신 실패 (ID: {client_id}): {str(e)}")
                logger.exception(e)
                break  # 예상치 못한 오류는 루프 종료
            
            # 시간 측정 시작
            start_time = time.time()
            
            # WebSocket 메시지 수신 로깅
            try:
                log_websocket_message(
                    message_content=data,
                    client_host=client_host
                )
            except Exception as e:
                logger.error(f"[WebSocket] 메시지 로깅 실패: {str(e)}")
            
            response = f"[{client_id}] 서버 응답: {data}"
            try:
                await websocket_service.send_personal_message(response, websocket)
            except:
                # 메시지 전송 실패 시 연결이 끊어진 것으로 간주
                break
            
            # 시간 측정 종료
            duration = time.time() - start_time
            
            # WebSocket 응답 전송 로깅
            try:
                log_websocket_response(
                    response=response,
                    client_host=client_host,
                    duration=duration
                )
            except Exception as e:
                logger.error(f"[WebSocket] 응답 로깅 실패: {str(e)}")
            
    except WebSocketDisconnect:
        pass  # 이미 루프에서 처리됨
    except Exception as e:
        logger.error(f"[WebSocket] 오류 발생 (ID: {client_id}): {str(e)}")
        logger.exception(e)
    finally:
        # 항상 연결 정리
        try:
            websocket_service.disconnect(websocket)
            log_websocket_disconnect(
                client_host=client_host,
                connection_count=websocket_service.get_connection_count()
            )
        except Exception as e:
            logger.error(f"[WebSocket] 연결 정리 중 오류: {str(e)}")

