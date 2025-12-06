"""구조화된 로깅 유틸리티"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from colorama import init, Fore, Style, Back

# Windows에서 colorama 초기화
init(autoreset=True)


# ==================== JSON 스키마 정의 ====================

class APILogSchema(BaseModel):
    """API 요청/응답 로그 스키마"""
    timestamp: str = Field(..., description="타임스탬프")
    log_type: str = Field(..., description="로그 타입: api_request 또는 api_response")
    method: str = Field(..., description="HTTP 메서드")
    path: str = Field(..., description="요청 경로")
    status_code: Optional[int] = Field(None, description="HTTP 상태 코드")
    process_time: Optional[float] = Field(None, description="처리 시간 (초)")
    client_host: Optional[str] = Field(None, description="클라이언트 호스트")
    request_headers: Optional[Dict[str, str]] = Field(None, description="요청 헤더")
    request_body: Optional[Any] = Field(None, description="요청 본문")
    response_body: Optional[Any] = Field(None, description="응답 본문")
    error: Optional[str] = Field(None, description="에러 메시지")


class WebSocketLogSchema(BaseModel):
    """WebSocket 로그 스키마"""
    timestamp: str = Field(..., description="타임스탬프")
    log_type: str = Field(..., description="로그 타입: ws_connect, ws_message, ws_response, ws_disconnect")
    event_type: str = Field(..., description="이벤트 타입")
    client_host: Optional[str] = Field(None, description="클라이언트 호스트")
    origin: Optional[str] = Field(None, description="Origin 헤더")
    message_content: Optional[str] = Field(None, description="메시지 내용")
    response: Optional[str] = Field(None, description="응답 내용")
    connection_count: Optional[int] = Field(None, description="현재 연결 수")
    error: Optional[str] = Field(None, description="에러 메시지")


class LLMLogSchema(BaseModel):
    """LLM 로그 스키마"""
    timestamp: str = Field(..., description="타임스탬프")
    log_type: str = Field(..., description="로그 타입: llm_request 또는 llm_response")
    api_endpoint: str = Field(..., description="API 엔드포인트")
    model: str = Field(..., description="사용 모델")
    temperature: Optional[float] = Field(None, description="Temperature 설정")
    max_tokens: Optional[int] = Field(None, description="Max tokens 설정")
    prompt: Optional[List[Dict[str, str]]] = Field(None, description="프롬프트 메시지 리스트")
    request_headers: Optional[Dict[str, str]] = Field(None, description="요청 헤더")
    response_content: Optional[str] = Field(None, description="응답 내용")
    usage_info: Optional[Dict[str, int]] = Field(None, description="사용량 정보 (prompt_tokens, completion_tokens, total_tokens)")
    error: Optional[str] = Field(None, description="에러 메시지")


# ==================== 콘솔 출력 포맷터 ====================

def format_json_pretty(data: Dict[str, Any], indent: int = 2) -> str:
    """JSON을 예쁘게 포맷팅 (MongoDB 저장용)"""
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def truncate_text(text: str, max_length: int = 100) -> str:
    """텍스트를 최대 길이로 자르기"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_headers(headers: Optional[Dict[str, str]], max_items: int = 5) -> str:
    """헤더를 포맷팅"""
    if not headers:
        return "None"
    
    items = list(headers.items())[:max_items]
    formatted = ", ".join([f"{k}: {truncate_text(str(v), 30)}" for k, v in items])
    if len(headers) > max_items:
        formatted += f" ... (+{len(headers) - max_items} more)"
    return formatted


def format_timestamp() -> str:
    """현재 시간을 간단한 형식으로 포맷팅"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ==================== API 로거 함수 ====================

def log_api_request(
    method: str,
    path: str,
    client_host: Optional[str] = None,
    request_headers: Optional[Dict[str, str]] = None,
    request_body: Optional[Any] = None
):
    """API 요청 로깅"""
    log_data = APILogSchema(
        timestamp=datetime.now().isoformat(),
        log_type="api_request",
        method=method,
        path=path,
        client_host=client_host,
        request_headers=request_headers,
        request_body=request_body
    )
    
    # JSON 데이터 (MongoDB 저장용)
    json_data = log_data.model_dump(exclude_none=True)
    
    # 콘솔 출력 (통일된 형식)
    timestamp = format_timestamp()
    print(f"{Fore.CYAN}REQUEST {timestamp}{Style.RESET_ALL}")
    print(f"  path: {method} {path} from {client_host or 'Unknown'}")
    if request_headers:
        print(f"  header: {format_headers(request_headers)}")


def log_api_response(
    method: str,
    path: str,
    status_code: int,
    process_time: float,
    client_host: Optional[str] = None,
    response_body: Optional[Any] = None,
    error: Optional[str] = None
):
    """API 응답 로깅"""
    log_data = APILogSchema(
        timestamp=datetime.now().isoformat(),
        log_type="api_response",
        method=method,
        path=path,
        status_code=status_code,
        process_time=round(process_time, 4),
        client_host=client_host,
        response_body=response_body,
        error=error
    )
    
    # JSON 데이터 (MongoDB 저장용)
    json_data = log_data.model_dump(exclude_none=True)
    
    # 상태 코드에 따라 색상 변경
    if status_code >= 500:
        color = Fore.RED
    elif status_code >= 400:
        color = Fore.YELLOW
    else:
        color = Fore.GREEN
    
    # 콘솔 출력 (통일된 형식)
    timestamp = format_timestamp()
    print(f"{color}RESPONSE {timestamp}{Style.RESET_ALL}")
    print(f"  path: {method} {path} from {client_host or 'Unknown'} → {status_code} ({process_time:.3f}s)")
    if error:
        print(f"  error: {truncate_text(error, 100)}")


# ==================== WebSocket 로거 함수 ====================

def log_websocket_connect(
    client_host: Optional[str] = None,
    origin: Optional[str] = None,
    connection_count: Optional[int] = None
):
    """WebSocket 연결 로깅"""
    log_data = WebSocketLogSchema(
        timestamp=datetime.now().isoformat(),
        log_type="ws_connect",
        event_type="connect",
        client_host=client_host,
        origin=origin,
        connection_count=connection_count
    )
    
    # JSON 데이터 (MongoDB 저장용)
    json_data = log_data.model_dump(exclude_none=True)
    
    # 콘솔 출력 (통일된 형식)
    timestamp = format_timestamp()
    print(f"{Fore.GREEN}WS_CONNECT {timestamp}{Style.RESET_ALL}")
    print(f"  path: WS /ws from {client_host or 'Unknown'}")
    if origin:
        print(f"  header: origin: {origin}")
    if connection_count is not None:
        print(f"  connections: {connection_count}")


def log_websocket_message(
    message_content: str,
    client_host: Optional[str] = None
):
    """WebSocket 메시지 수신 로깅"""
    log_data = WebSocketLogSchema(
        timestamp=datetime.now().isoformat(),
        log_type="ws_message",
        event_type="message",
        client_host=client_host,
        message_content=message_content
    )
    
    # JSON 데이터 (MongoDB 저장용)
    json_data = log_data.model_dump(exclude_none=True)
    
    # 콘솔 출력 (통일된 형식)
    timestamp = format_timestamp()
    print(f"{Fore.GREEN}WS_MESSAGE {timestamp}{Style.RESET_ALL}")
    print(f"  path: WS /ws from {client_host or 'Unknown'}")
    print(f"  message: {truncate_text(message_content, 100)}")


def log_websocket_response(
    response: str,
    client_host: Optional[str] = None,
    duration: Optional[float] = None
):
    """WebSocket 응답 전송 로깅"""
    log_data = WebSocketLogSchema(
        timestamp=datetime.now().isoformat(),
        log_type="ws_response",
        event_type="response",
        client_host=client_host,
        response=response
    )
    
    # JSON 데이터 (MongoDB 저장용)
    json_data = log_data.model_dump(exclude_none=True)
    
    # 콘솔 출력 (통일된 형식)
    timestamp = format_timestamp()
    print(f"{Fore.GREEN}WS_RESPONSE {timestamp}{Style.RESET_ALL}")
    print(f"  path: WS /ws to {client_host or 'Unknown'}")
    if duration is not None:
        print(f"  duration: {duration:.3f}s")
    print(f"  response: {truncate_text(response, 100)}")


def log_websocket_disconnect(
    client_host: Optional[str] = None,
    connection_count: Optional[int] = None
):
    """WebSocket 연결 해제 로깅"""
    log_data = WebSocketLogSchema(
        timestamp=datetime.now().isoformat(),
        log_type="ws_disconnect",
        event_type="disconnect",
        client_host=client_host,
        connection_count=connection_count
    )
    
    # JSON 데이터 (MongoDB 저장용)
    json_data = log_data.model_dump(exclude_none=True)
    
    # 콘솔 출력 (통일된 형식)
    timestamp = format_timestamp()
    print(f"{Fore.YELLOW}WS_DISCONNECT {timestamp}{Style.RESET_ALL}")
    print(f"  path: WS /ws from {client_host or 'Unknown'}")
    if connection_count is not None:
        print(f"  connections: {connection_count} remaining")


# ==================== LLM 로거 함수 ====================

def log_llm_request(
    api_endpoint: str,
    model: str,
    prompt: Optional[List[Dict[str, str]]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    request_headers: Optional[Dict[str, str]] = None
):
    """LLM 요청 로깅"""
    log_data = LLMLogSchema(
        timestamp=datetime.now().isoformat(),
        log_type="llm_request",
        api_endpoint=api_endpoint,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt=prompt,
        request_headers=request_headers
    )
    
    # JSON 데이터 (MongoDB 저장용)
    json_data = log_data.model_dump(exclude_none=True)
    
    # 콘솔 출력 (통일된 형식)
    timestamp = format_timestamp()
    print(f"{Fore.YELLOW}LLM_REQUEST {timestamp}{Style.RESET_ALL}")
    print(f"  path: {api_endpoint} [{model}]")
    if temperature or max_tokens:
        settings = []
        if temperature is not None:
            settings.append(f"temp={temperature}")
        if max_tokens:
            settings.append(f"max_tokens={max_tokens}")
        print(f"  settings: {', '.join(settings)}")
    if request_headers:
        print(f"  header: {format_headers(request_headers)}")
    if prompt:
        user_msg = ""
        for msg in reversed(prompt):
            if msg.get("role") == "user":
                user_msg = truncate_text(msg.get("content", ""), 100)
                break
        if user_msg:
            print(f"  prompt: {user_msg}")


def log_llm_response(
    api_endpoint: str,
    model: str,
    response_content: str,
    usage_info: Optional[Dict[str, int]] = None,
    error: Optional[str] = None,
    duration: Optional[float] = None
):
    """LLM 응답 로깅"""
    log_data = LLMLogSchema(
        timestamp=datetime.now().isoformat(),
        log_type="llm_response",
        api_endpoint=api_endpoint,
        model=model,
        response_content=response_content,
        usage_info=usage_info,
        error=error
    )
    
    # JSON 데이터 (MongoDB 저장용)
    json_data = log_data.model_dump(exclude_none=True)
    
    # 에러 여부에 따라 색상 변경
    color = Fore.RED if error else Fore.YELLOW
    
    # 콘솔 출력 (통일된 형식)
    timestamp = format_timestamp()
    print(f"{color}LLM_RESPONSE {timestamp}{Style.RESET_ALL}")
    print(f"  path: {api_endpoint} [{model}]")
    if duration is not None:
        print(f"  duration: {duration:.3f}s")
    if error:
        print(f"  error: {truncate_text(error, 100)}")
    else:
        if usage_info:
            print(f"  usage: {usage_info.get('total_tokens', 0)} tokens (prompt: {usage_info.get('prompt_tokens', 0)}, completion: {usage_info.get('completion_tokens', 0)})")
        if response_content:
            print(f"  response: {truncate_text(response_content, 100)}")


def log_error(message: str, exception: Exception) -> None:
    """에러를 로깅함
    
    Args:
        message: 에러 메시지 (예: "Settings validation failed")
        exception: 발생한 예외 객체
    """
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    logger.error(f"✗ {message}: {exception}")
    logger.error(traceback.format_exc())


# ==================== SQL 쿼리 로거 함수 ====================

def log_sql_query(query: str, duration: Optional[float] = None):
    """SQL 쿼리 로깅
    
    Args:
        query: SQL 쿼리 문자열
        duration: 쿼리 실행 시간 (초, 선택적)
    """
    timestamp = format_timestamp()
    
    # SQL 쿼리를 예쁘게 포맷팅 (너무 길면 자르기)
    formatted_query = truncate_text(query, 500)
    
    print(f"{Fore.MAGENTA}SQL {timestamp}{Style.RESET_ALL}")
    print(f"  path: SQL query")
    print(f"  query: {formatted_query}")
    if duration is not None:
        print(f"  duration: {duration:.3f}s")