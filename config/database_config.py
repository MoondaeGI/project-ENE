import logging
from urllib.parse import quote_plus
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
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

# SQL 쿼리 로깅을 위한 커스텀 핸들러 설정
def setup_sql_logging():
    """SQLAlchemy 쿼리 로깅을 커스텀 로거로 리다이렉트"""
    from utils.logs.logger import log_sql_query
    import time
    
    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.INFO)
    
    # 기존 핸들러 제거 (echo=True의 기본 핸들러)
    sql_logger.handlers = []
    
    # 커스텀 핸들러 추가
    class SQLQueryHandler(logging.Handler):
        def emit(self, record):
            if record.levelno == logging.INFO:
                # SQL 쿼리 로깅
                message = record.getMessage()
                if any(message.strip().upper().startswith(cmd) for cmd in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'BEGIN', 'COMMIT']):
                    log_sql_query(message)
    
    sql_logger.addHandler(SQLQueryHandler())
    
    # 쿼리 실행 시간 측정을 위한 이벤트 리스너
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()
    
    @event.listens_for(Engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - context._query_start_time
        log_sql_query(statement, duration=total)

engine = create_engine(
    DATABASE_URL, 
    connect_args={"client_encoding": "UTF8"},
)

# SQL 쿼리 로깅 설정
setup_sql_logging()

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base 클래스 (모든 모델이 상속받을 클래스)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit();
    except Exception as e:
        db.rollback();
        raise e;
    finally:
        db.close()

