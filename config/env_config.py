"""환경 변수 설정"""
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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
    server_port: int
    secret_key: str  # 필수: 환경 변수에서 주입되어야 함
    openai_api_key: str  # 필수: 환경 변수에서 주입되어야 함
    
    def model_post_init(self, __context) -> None:
        # 필수 환경 변수 검증 - 값이 없으면 예외를 던져 서버 시작 실패
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. 서버를 시작할 수 없습니다.")
        
        if not self.secret_key:
            raise ValueError("SECRET_KEY 환경 변수가 설정되지 않았습니다. 서버를 시작할 수 없습니다.")

settings = Settings()

