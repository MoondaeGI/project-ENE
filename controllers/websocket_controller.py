"""WebSocket 컨트롤러"""
import logging
import time
from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from sqlalchemy.orm import Session
from config.database_config import SessionLocal
from services import websocket_service, llm_service
from services.message_service import MessageService
from services.reflection_service import ReflectionService
from services.last_reflected_id_service import LastReflectedIdService
from schemas.message import PersonMessageCreate, AIMessageCreate
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
        await websocket_service.send_personal_message("서버에 연결되었습니다! 질문을 입력해주세요.", websocket)
        
        while True:
            try:
                # 클라이언트로부터 메시지 수신
                user_message = await websocket.receive_text()
            except WebSocketDisconnect:
                # 연결이 정상적으로 끊어진 경우
                break
            except UnicodeDecodeError as e:
                logger.error(f"[WebSocket] 메시지 디코딩 실패 (UTF-8): {str(e)}")
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
            
            # 서비스 인스턴스 생성
            db = SessionLocal()
            person_id = 1
            
            try:
                message_service = MessageService(db)
                reflection_service = ReflectionService(db)
                last_reflected_service = LastReflectedIdService(db)
                
                # 1. 사용자 메시지 저장 → message_id 얻기
                safe_content = user_message.encode('utf-8', errors='replace').decode('utf-8')
                person_message_data = PersonMessageCreate(person_id=person_id, content=safe_content)
                
                try:
                    person_message_response = message_service.create_person_message(person_message_data)
                    current_message_id = person_message_response.id
                    logger.info(f"[WebSocket] 사용자 메시지 저장 완료 - message_id: {current_message_id}")
                except (UnicodeEncodeError, UnicodeDecodeError) as e:
                    error_type = type(e).__name__
                    logger.error(f"[WebSocket] 메시지 저장 실패 ({error_type})")
                    continue
                except Exception as e:
                    error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                    logger.error(f"[WebSocket] 메시지 저장 실패: {error_msg}")
                    logger.exception(e)
                    continue
                
                # 2. 가장 최신의 reflection 가져오기
                latest_reflection = reflection_service.get_latest_reflection(person_id)
                reflection_summary = latest_reflection.summary if latest_reflection else None
                
                # 3. last_reflected_id의 message_id 확인
                last_message_id = last_reflected_service.get_last_reflected_message_id(person_id)
                
                # 4. last_message_id 이후의 모든 메시지 가져오기
                messages = message_service.get_messages_after(last_message_id, person_id)
                message_contents = [msg.content for msg in messages]
                
                # 5. LLM 응답 생성 (reflection과 message list 포함)
                try:
                    await websocket_service.send_personal_message(
                        "🤔 생각 중...",
                        websocket
                    )
                except:
                    break
                
                if llm_service.client is None:
                    llm_response = "⚠️ LLM 서비스가 초기화되지 않았습니다."
                else:
                    try:
                        llm_response = await llm_service.generate_response_with_context(
                            user_message=user_message,
                            reflection=reflection_summary,
                            messages=message_contents
                        )
                    except Exception as e:
                        logger.error(f"[WebSocket] LLM 응답 생성 실패: {str(e)}")
                        llm_response = "⚠️ 응답 생성 중 오류가 발생했습니다."
                
                # 6. LLM 응답 전송 (먼저 전송)
                try:
                    await websocket_service.send_personal_message(llm_response, websocket)
                except:
                    # 메시지 전송 실패 시 연결이 끊어진 것으로 간주
                    break
                
                # 7. LLM 응답을 message에 저장
                safe_ai_content = llm_response.encode('utf-8', errors='replace').decode('utf-8')
                ai_message_data = AIMessageCreate(content=safe_ai_content)
                
                try:
                    ai_message_response = message_service.create_ai_message(ai_message_data)
                    logger.info(f"[WebSocket] AI 메시지 저장 완료 - message_id: {ai_message_response.id}")
                except (UnicodeEncodeError, UnicodeDecodeError) as e:
                    error_type = type(e).__name__
                    logger.error(f"[WebSocket] AI 메시지 저장 실패 ({error_type})")
                except Exception as e:
                    error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                    logger.error(f"[WebSocket] AI 메시지 저장 실패: {error_msg}")
                    logger.exception(e)
                
                # 8. 현재 최신 message_id와 last_message_id 차이가 10 이상이면 reflection 생성
                if current_message_id - last_message_id >= 10:
                    try:
                        # 요약에 사용할 message_ids 추출
                        message_ids = [msg.id for msg in messages]
                        
                        # LLM으로 요약 생성 (트랜잭션 밖에서 수행)
                        message_contents = [msg.content for msg in messages]
                        summary = await llm_service.generate_summary(reflection_summary, message_contents)
                        
                        # 트랜잭션으로 reflection 생성 및 모든 업데이트 처리
                        reflection_service.create_reflection_with_messages(
                            summary=summary,
                            message_ids=message_ids,
                            current_message_id=current_message_id,
                            person_id=person_id
                        )
                        logger.info(f"[WebSocket] Reflection 생성 완료 - message_id: {current_message_id}")
                    except Exception as e:
                        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                        logger.error(f"[WebSocket] Reflection 생성 실패: {error_msg}")
                        logger.exception(e)
                
            finally:
                db.close()
            
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

