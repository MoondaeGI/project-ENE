# Tools Reference

이 프로젝트에서 사용하는 MCP 서버 및 CLI 도구 목록입니다.

## MCP 서버

| 이름 | 용도 |
|------|------|
| `postgres` | PostgreSQL 직접 쿼리 — 스키마 확인, 데이터 조회, 마이그레이션 검증 |
| `filesystem` | 프로젝트 파일 읽기/쓰기 |
| `github` | PR, 이슈, 코드 리뷰 관리 |
| `obsidian` | Obsidian vault 노트 읽기/쓰기 — `.claude/docs/` 동기화에 사용 |

## CLI 도구

### 개발

| 커맨드 | 용도 | 예시 |
|--------|------|------|
| `alembic` | DB 마이그레이션 생성 및 적용 | `alembic revision --autogenerate -m "add index"` |
| `uvicorn` | FastAPI 개발 서버 실행 | `uvicorn src.api.main:app --reload` |
| `pytest` | 테스트 실행 | `pytest tests/unit/ -v --cov=src` |
| `psql` | PostgreSQL 직접 접속 | `psql $DATABASE_URL` |

### 인프라 & 배포

| 커맨드 | 용도 | 예시 |
|--------|------|------|
| `docker compose` | 로컬 DB/서비스 실행 | `docker compose up -d postgres` |
| `aws` | AWS 리소스 관리 | `aws ecs deploy ...` |

### 테스트

| 라이브러리 | 용도 |
|-----------|------|
| `pytest` | 테스트 러너 |
| `pytest-asyncio` | `async/await` 테스트 지원 (`asyncio_mode = "auto"`) |
| `pytest-cov` | 커버리지 측정 (`--cov=src --cov-report=term-missing`) |
| `testcontainers` | 통합 테스트용 실제 PostgreSQL 컨테이너 실행 |
| `httpx` | FastAPI 비동기 테스트 클라이언트 (`AsyncClient`) |

```bash
# 단위 테스트
pytest tests/unit/ -v

# 커버리지 포함
pytest tests/unit/ --cov=src --cov-report=term-missing -v

# 통합 테스트
pytest tests/integration/ -v --timeout=30
```

### 문서

| 커맨드 | 용도 | 예시 |
|--------|------|------|
| `obsidian-git` | Obsidian vault git 동기화 | vault 내부에서 자동 실행 |
