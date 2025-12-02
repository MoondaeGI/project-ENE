"""환경 변수 설정"""
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def validate_required_field(value: str | int | None, env_name: str) -> None:
    """필수 환경 변수 검증 - 값이 없으면 예외를 던져 서버 시작 실패"""
    if not value:
        raise ValueError(f"{env_name} 환경 변수가 설정되지 않았습니다. 서버를 시작할 수 없습니다.")


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
    
    # 데이터베이스 설정
    db_host: str  # 필수: 데이터베이스 호스트
    db_port: int  # 필수: 데이터베이스 포트
    db_user: str  # 필수: 데이터베이스 사용자
    db_password: str  # 필수: 데이터베이스 비밀번호
    db_name: str  # 필수: 데이터베이스 이름
    
    def model_post_init(self, __context) -> None:
        # 필수 환경 변수 검증
        validate_required_field(self.openai_api_key, "OPENAI_API_KEY")
        validate_required_field(self.secret_key, "SECRET_KEY")
        
        # 데이터베이스 설정 검증
        validate_required_field(self.db_host, "DB_HOST")
        validate_required_field(self.db_port, "DB_PORT")
        validate_required_field(self.db_user, "DB_USER")
        validate_required_field(self.db_password, "DB_PASSWORD")
        validate_required_field(self.db_name, "DB_NAME")

settings = Settings()

