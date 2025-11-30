"""설정 모듈"""
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# 전역 settings 인스턴스 (초기값은 None)
_settings: "Settings | None" = None


class Settings(BaseSettings):
    """애플리케이션 설정"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # 대소문자 구분 안 함 (SERVER_PORT 또는 server_port 모두 가능)
    )
    
    app_name: str = "FastAPI REST API"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    
    # 환경 변수에서 읽어올 값들
    server_port: int = 8000
    secret_key: str = "dev-secret-key-change-in-production"  # 기본값 추가
    openai_api_key: str = ""
    
    def model_post_init(self, __context) -> None:
        """설정 검증 로직"""
        # 필수 환경 변수 검증
        if self.openai_api_key == "":
            logger.warning("OpenAI API 키가 설정되지 않았습니다. LLM 기능이 동작하지 않을 수 있습니다.")
        
        if self.secret_key == "dev-secret-key-change-in-production":
            logger.warning("프로덕션 환경에서는 반드시 SECRET_KEY를 변경해주세요.")


def get_settings() -> Settings:
    """Settings 인스턴스를 가져옵니다 (싱글톤 패턴)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def validate_settings() -> Settings:
    """Settings를 로드하고 검증합니다. 서버 시작 시 가장 먼저 호출되어야 합니다."""
    settings = get_settings()
    return settings


# 모듈 레벨에서 기본 인스턴스 생성 (하위 호환성)
settings = get_settings()
