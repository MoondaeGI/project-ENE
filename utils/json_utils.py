"""JSON 블록 추출 등 JSON 관련 유틸리티"""


def extract_json_block(text: str) -> str:
    """
    텍스트에서 첫 번째 '{' 부터 마지막 '}' 까지 추출하여 JSON 문자열로 반환.
    마크다운 코드블록이나 설명이 포함된 LLM 응답에서 JSON만 뽑을 때 사용.

    Args:
        text: 원본 텍스트 (예: LLM 응답 전체)

    Returns:
        추출된 JSON 구간 문자열. '{' 또는 '}'가 없으면 원본 text 그대로 반환.
    """
    if not text or not text.strip():
        return text or ""
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text
