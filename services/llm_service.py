"""LLM 서비스 (OpenAI)"""
import logging
import time
from typing import Optional, List, Dict
from openai import OpenAI
from config import settings
from utils.logs.logger import log_llm_request, log_llm_response
from prompts.prompt_loader import get_system_prompt

logger = logging.getLogger(__name__)


class LLMService:
    """OpenAI LLM 서비스"""
    
    def __init__(self):
        """LLM 서비스 초기화"""
        if not settings.openai_api_key:
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=settings.openai_api_key)
            except Exception as e:
                logger.error(f"OpenAI 클라이언트 초기화 실패: {e}")
                logger.exception(e)
                self.client = None
    
    async def generate_response(
        self, 
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7
    ) -> str:
        """
        사용자 메시지에 대한 LLM 응답 생성
        
        Args:
            user_message: 사용자 메시지
            conversation_history: 대화 히스토리 (선택적)
            model: 사용할 모델 이름
            temperature: 응답 창의성 (0.0 ~ 1.0)
            
        Returns:
            LLM 응답 텍스트
        """
        if not self.client:
            return "⚠️ OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 추가해주세요."
        
        try:
            # 대화 히스토리 구성
            messages = []
            
            # 시스템 프롬프트 (파일에서 읽어옴)
            system_prompt = get_system_prompt()
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
            # 대화 히스토리 추가
            if conversation_history:
                messages.extend(conversation_history)
            
            # 현재 사용자 메시지 추가
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # API 엔드포인트
            api_endpoint = "https://api.openai.com/v1/chat/completions"
            max_tokens = 1000
            
            # 요청 헤더 (민감한 정보 제외)
            request_headers = {
                "Content-Type": "application/json"
            }
            if settings.openai_api_key:
                request_headers["Authorization"] = f"Bearer {settings.openai_api_key[:10]}..."
            
            # LLM 요청 로깅
            log_llm_request(
                api_endpoint=api_endpoint,
                model=model,
                prompt=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                request_headers=request_headers
            )
            
            # 시간 측정 시작
            start_time = time.time()
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 시간 측정 종료
            duration = time.time() - start_time
            
            # 응답 추출
            llm_response = response.choices[0].message.content
            
            # 사용량 정보 추출
            usage_info = None
            if hasattr(response, 'usage') and response.usage:
                usage_info = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            # LLM 응답 로깅
            log_llm_response(
                api_endpoint=api_endpoint,
                model=model,
                response_content=llm_response,
                usage_info=usage_info,
                duration=duration
            )
            
            return llm_response
            
        except Exception as e:
            error_msg = f"LLM 응답 생성 중 오류 발생: {str(e)}"
            logger.error(f"[LLM] {error_msg}")
            logger.exception(e)
            
            # 에러 로깅
            api_endpoint = "https://api.openai.com/v1/chat/completions"
            log_llm_response(
                api_endpoint=api_endpoint,
                model=model,
                response_content=None,
                error=error_msg
            )
            
            return f"⚠️ {error_msg}"


# 싱글톤 인스턴스 (다른 서비스들과 동일하게 모듈 레벨에서 바로 초기화)
# app/main.py에서 settings가 먼저 로드되고 검증된 후 이 모듈이 import되므로
# settings는 이미 준비된 상태입니다.
llm_service = LLMService()

