"""LLM 서비스 (OpenAI)"""
import logging
from typing import Optional, List, Dict
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """OpenAI LLM 서비스"""
    
    def __init__(self):
        """LLM 서비스 초기화"""
        if not settings.openai_api_key:
            logger.warning("OpenAI API 키가 설정되지 않았습니다.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI LLM 서비스 초기화 완료")
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
            
            # 시스템 프롬프트 (선택적)
            messages.append({
                "role": "system",
                "content": "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 명확하고 정확하게 답변해주세요."
            })
            
            # 대화 히스토리 추가
            if conversation_history:
                messages.extend(conversation_history)
            
            # 현재 사용자 메시지 추가
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            logger.info(f"[LLM] 요청 생성 - 모델: {model}, 메시지 길이: {len(user_message)}")
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            
            # 응답 추출
            llm_response = response.choices[0].message.content
            logger.info(f"[LLM] 응답 생성 완료 - 길이: {len(llm_response)}")
            
            return llm_response
            
        except Exception as e:
            error_msg = f"LLM 응답 생성 중 오류 발생: {str(e)}"
            logger.error(f"[LLM] {error_msg}")
            logger.exception(e)
            return f"⚠️ {error_msg}"


# 싱글톤 인스턴스 (다른 서비스들과 동일하게 모듈 레벨에서 바로 초기화)
# app/main.py에서 settings가 먼저 로드되고 검증된 후 이 모듈이 import되므로
# settings는 이미 준비된 상태입니다.
llm_service = LLMService()

