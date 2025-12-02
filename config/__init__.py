"""설정 모듈"""
import logging
from pydantic import Field, field_validator
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
    cors_origins: list[str]  # 필수: 쉼표로 구분된 문자열 (예: "http://localhost:3000,http://localhost:8080")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origin(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return []
    
    def model_post_init(self, __context) -> None:
        # 필수 환경 변수 검증 - 값이 없으면 예외를 던져 서버 시작 실패
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. 서버를 시작할 수 없습니다.")
        
        if not self.secret_key:
            raise ValueError("SECRET_KEY 환경 변수가 설정되지 않았습니다. 서버를 시작할 수 없습니다.")

        if not self.cors_origins or len(self.cors_origins) == 0:
            raise ValueError("CORS_ORIGIN 환경 변수가 설정되지 않았습니다. 서버를 시작할 수 없습니다.")

settings = Settings()


