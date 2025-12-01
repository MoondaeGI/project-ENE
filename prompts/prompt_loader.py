"""프롬프트 로더 모듈"""
import os
from pathlib import Path
from typing import Optional


def get_system_prompt() -> str:
    """
    시스템 프롬프트를 파일에서 읽어옵니다.
    
    Returns:
        시스템 프롬프트 문자열
    """
    # 현재 파일의 디렉토리 기준으로 prompts 디렉토리 찾기
    current_dir = Path(__file__).parent
    prompt_file = current_dir / "system_prompt.txt"
    
    try:
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        else:
            # 파일이 없으면 기본 프롬프트 반환
            return "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 명확하고 정확하게 답변해주세요."
    except Exception as e:
        # 파일 읽기 실패 시 기본 프롬프트 반환
        return "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 명확하고 정확하게 답변해주세요."

