"""LLM 서비스 (OpenAI)"""
import json
import logging
import time
from typing import Optional, List, Dict, Tuple, Any
from openai import OpenAI
from config import settings
from utils.json_utils import extract_json_block
from utils.logs.logger import log_llm_request, log_llm_response
from prompts.prompt_loader import (
    get_system_prompt,
    get_summary_system_prompt,
    get_summary_user_prompt_template,
    get_tag_create_system_prompt,
    get_tag_create_user_prompt_template,
)

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
        model: str = "gpt-4o-mini",
        temperature: float = 0.7
    ) -> str:
        """
        사용자 메시지에 대한 LLM 응답 생성
        
        Args:
            user_message: 사용자 메시지
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
    
    async def generate_response_with_context(
        self,
        user_message: str,
        reflection: Optional[str],
        messages: List[str],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7
    ) -> str:
        """
        reflection과 message list를 포함한 컨텍스트로 응답 생성
        
        Args:
            user_message: 사용자 메시지
            reflection: 이전 reflection 요약 (없으면 None)
            messages: 이전 메시지 리스트
            model: 사용할 모델 이름
            temperature: 응답 창의성 (0.0 ~ 1.0)
            
        Returns:
            LLM 응답 텍스트
        """
        if not self.client:
            return "⚠️ OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 추가해주세요."
        
        try:
            messages_list = []
            
            # 시스템 프롬프트
            system_prompt = get_system_prompt()
            messages_list.append({
                "role": "system",
                "content": system_prompt
            })
            
            # 이전 reflection이 있으면 컨텍스트로 추가
            if reflection:
                messages_list.append({
                    "role": "system",
                    "content": f"이전 대화 요약:\n{reflection}"
                })
            
            # 이전 메시지들을 컨텍스트로 추가
            if messages:
                context = "\n".join([f"- {msg}" for msg in messages])
                messages_list.append({
                    "role": "system",
                    "content": f"이전 대화 내용:\n{context}"
                })
            
            # 현재 사용자 메시지 추가
            messages_list.append({
                "role": "user",
                "content": user_message
            })
            
            api_endpoint = "https://api.openai.com/v1/chat/completions"
            max_tokens = 1000
            
            request_headers = {
                "Content-Type": "application/json"
            }
            if settings.openai_api_key:
                request_headers["Authorization"] = f"Bearer {settings.openai_api_key[:10]}..."
            
            log_llm_request(
                api_endpoint=api_endpoint,
                model=model,
                prompt=messages_list,
                temperature=temperature,
                max_tokens=max_tokens,
                request_headers=request_headers
            )
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages_list,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            duration = time.time() - start_time
            llm_response = response.choices[0].message.content
            
            usage_info = None
            if hasattr(response, 'usage') and response.usage:
                usage_info = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
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
            
            api_endpoint = "https://api.openai.com/v1/chat/completions"
            log_llm_response(
                api_endpoint=api_endpoint,
                model=model,
                response_content=None,
                error=error_msg
            )
            
            return f"⚠️ {error_msg}"
    
    async def generate_summary(
        self,
        reflection: Optional[str],
        messages: List[str],
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        messages_with_roles: Optional[List[Tuple[str, str]]] = None,
    ) -> str:
        """
        reflection과 message list를 요약
        
        Args:
            reflection: 이전 reflection 요약 (없으면 None)
            messages: 요약할 메시지 리스트
            model: 사용할 모델 이름
            temperature: 응답 창의성 (요약이므로 낮게 설정)
            
        Returns:
            요약 텍스트
        """
        if not self.client:
            return "⚠️ OpenAI API 키가 설정되지 않았습니다."
        
        try:
            messages_list = []
            messages_list.append({
                "role": "system",
                "content": get_summary_system_prompt()
            })
            if reflection:
                messages_list.append({
                    "role": "system",
                    "content": f"이전 요약:\n{reflection}"
                })
            if messages_with_roles:
                context_lines = []
                for role, content in messages_with_roles:
                    role_label = "PERSON" if role.upper() == "PERSON" else "AI"
                    context_lines.append(f"[{role_label}] {content}")
                context = "\n".join(context_lines)
            elif messages:
                context = "\n".join([f"- {msg}" for msg in messages])
            else:
                return "요약할 메시지가 없습니다."
            user_template = get_summary_user_prompt_template()
            messages_list.append({
                "role": "user",
                "content": user_template.format(context=context)
            })
            
            api_endpoint = "https://api.openai.com/v1/chat/completions"
            max_tokens = 500  # 요약이므로 토큰 수 제한
            
            request_headers = {
                "Content-Type": "application/json"
            }
            if settings.openai_api_key:
                request_headers["Authorization"] = f"Bearer {settings.openai_api_key[:10]}..."
            
            log_llm_request(
                api_endpoint=api_endpoint,
                model=model,
                prompt=messages_list,
                temperature=temperature,
                max_tokens=max_tokens,
                request_headers=request_headers
            )
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages_list,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            duration = time.time() - start_time
            summary = response.choices[0].message.content
            
            usage_info = None
            if hasattr(response, 'usage') and response.usage:
                usage_info = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            log_llm_response(
                api_endpoint=api_endpoint,
                model=model,
                response_content=summary,
                usage_info=usage_info,
                duration=duration
            )
            
            return summary
            
        except Exception as e:
            error_msg = f"요약 생성 중 오류 발생: {str(e)}"
            logger.error(f"[LLM] {error_msg}")
            logger.exception(e)
            
            api_endpoint = "https://api.openai.com/v1/chat/completions"
            log_llm_response(
                api_endpoint=api_endpoint,
                model=model,
                response_content=None,
                error=error_msg
            )
            
            return f"⚠️ {error_msg}"

    async def select_or_create_tags(
        self,
        existing_tags: List[Dict[str, Any]],
        content: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
        max_tags: int = 5,
    ) -> Dict[str, Any]:
        """
        내용에 맞는 태그를 기존 태그에서 최대 5개 선택하거나, 없으면 새 태그 이름을 제안.
        Returns: {"selected_ids": [1, 2], "new_names": ["감정", "일상"]}
        """
        if not self.client:
            return {"selected_ids": [], "new_names": []}

        tags_line = "\n".join([f"- id: {t['id']}, tag: {t['tag']}" for t in existing_tags]) if existing_tags else "(없음)"
        system_prompt = get_tag_create_system_prompt()
        user_content = get_tag_create_user_prompt_template().format(
            tags_line=tags_line,
            content=content,
        )

        text = "{}"
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=temperature,
                max_tokens=300,
            )
            text = response.choices[0].message.content or "{}"
            text = extract_json_block(text)
            data = json.loads(text)
            selected_ids = list(data.get("selected_ids") or [])
            new_names = list(data.get("new_names") or [])
            # 최대 5개로 자르기
            total = len(selected_ids) + len(new_names)
            if total > max_tags:
                if len(selected_ids) >= max_tags:
                    selected_ids = selected_ids[:max_tags]
                    new_names = []
                else:
                    new_names = new_names[: max_tags - len(selected_ids)]
            return {"selected_ids": selected_ids, "new_names": new_names}
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"[LLM] 태그 선택 응답 파싱 실패: {e}, raw: {text[:200]}")
            return {"selected_ids": [], "new_names": []}
        except Exception as e:
            logger.error(f"[LLM] select_or_create_tags 실패: {e}")
            logger.exception(e)
            return {"selected_ids": [], "new_names": []}


llm_service = LLMService()

