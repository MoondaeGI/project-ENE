import logging
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.env_config import settings

logger = logging.getLogger(__name__)

# 데이터베이스 URL 구성
DATABASE_URL = f"postgresql://{quote_plus(settings.db_user)}:{quote_plus(settings.db_password)}@{settings.db_host}:{settings.db_port}/{quote_plus(settings.db_name)}"

# 로깅용 URL (비밀번호 마스킹)
def mask_password_in_url(url: str) -> str:
    """URL에서 비밀번호를 마스킹"""
    try:
        if '@' in url and ':' in url.split('@')[0]:
            parts = url.split('@')
            auth_part = parts[0]
            rest = '@' + parts[1] if len(parts) > 1 else ''
            if ':' in auth_part:
                user_part, password_part = auth_part.rsplit(':', 1)
                masked_url = f"{user_part}:****{rest}"
                return masked_url
    except Exception:
        pass
    return url

# DB URL 로깅 (비밀번호 마스킹)
masked_url = mask_password_in_url(DATABASE_URL)
logger.info(f"[Database] 연결 URL: {masked_url}")

# SQL 쿼리 로깅 비활성화 (필요 시 sql_logger.setLevel(logging.INFO) 및 핸들러 추가로 복구 가능)
def setup_sql_logging():
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


engine = create_engine(
    DATABASE_URL,
    connect_args={"client_encoding": "UTF8"},
    echo=False,
)

setup_sql_logging()

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base 클래스 (모든 모델이 상속받을 클래스)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

