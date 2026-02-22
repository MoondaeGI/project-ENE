"""프롬프트 로더 모듈"""
from pathlib import Path

# 파일 경로 -> 로드된 내용 (캐시)
_prompt_cache: dict[str, str] = {}


def _read_prompt_file(filename: str, default: str) -> str:
    """prompts 디렉토리에서 파일을 읽어 반환합니다. 한 번 읽은 내용은 캐시합니다. 실패 시 default 반환."""
    if filename in _prompt_cache:
        return _prompt_cache[filename]
    current_dir = Path(__file__).parent
    prompt_file = current_dir / filename
    try:
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            _prompt_cache[filename] = content
            return content
    except Exception:
        pass
    return default


def clear_prompt_cache() -> None:
    """캐시를 비웁니다. 테스트나 프롬프트 파일 수정 후 재로드가 필요할 때 사용."""
    _prompt_cache.clear()


def get_system_prompt() -> str:
    """채팅용 시스템 프롬프트 (ENE 캐릭터 등)."""
    default = "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 명확하고 정확하게 답변해주세요."
    return _read_prompt_file("system_prompt.txt", default)


def get_summary_system_prompt() -> str:
    """대화 요약용 시스템 프롬프트."""
    default = (
        "당신은 대화 내용을 요약하는 전문가입니다. "
        "주어진 대화에서 PERSON(사용자) 발화를 더 높은 비중으로 반영하여 "
        "핵심을 간결하고 명확하게 요약하세요. AI 응답은 보조 맥락으로만 사용하세요."
    )
    return _read_prompt_file("summary/summary_system_prompt.txt", default)


def get_tag_create_system_prompt() -> str:
    """태그 선택/생성용 시스템 프롬프트 (JSON 출력)."""
    default = (
        '당신은 주어진 내용을 분류하는 태그 선택기입니다. '
        '반드시 아래 JSON 형식으로만 답하세요. 다른 설명은 넣지 마세요.\n'
        '{"selected_ids": [기존_태그_id 배열, 최대 5개], "new_names": [새로 만들 태그 이름 배열]}\n'
        "규칙: 기존 태그로 충분하면 selected_ids만 채우고 new_names는 빈 배열. "
        "기존에 없는 개념이 필요하면 new_names에 새 태그 이름을 넣으세요. "
        "selected_ids와 new_names 합쳐서 최대 5개를 초과하지 마세요."
    )
    return _read_prompt_file("tag/tag_create_prompt.txt", default)


def get_tag_create_user_prompt_template() -> str:
    """태그 선택/생성용 유저 메시지 템플릿. {tags_line}, {content} 플레이스홀더 사용."""
    default = (
        "기존 태그 목록:\n{tags_line}\n\n"
        "내용:\n{content}\n\n"
        "위 내용에 맞는 태그를 선택하거나 새로 제안한 뒤, JSON만 출력하세요."
    )
    return _read_prompt_file("tag/tag_create_user_prompt_template.txt", default)


def get_summary_user_prompt_template() -> str:
    """요약용 유저 메시지 템플릿. {context} 플레이스홀더 사용."""
    default = "다음 대화를 요약해주세요. PERSON 발화를 우선적으로 반영하세요:\n\n{context}"
    return _read_prompt_file("summary/summary_user_prompt_template.txt", default)


def get_episode_create_prompt() -> str:
    """에피소드 분리/생성용 시스템 프롬프트."""
    default = (
        "다음은 사용자와 AI의 대화 로그이다. 이 대화를 의미 있는 사건 단위(episode)로 나누어라."
    )
    return _read_prompt_file("episode/episode_create_prompt.txt", default)



