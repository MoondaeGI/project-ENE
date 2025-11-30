# FastAPI REST API 서버

FastAPI를 사용한 MVC 패턴 기반 REST API 서버 (WebSocket 지원)

## 프로젝트 구조

```
.
├── app/                    # 애플리케이션 패키지
│   ├── __init__.py
│   └── main.py            # FastAPI 앱 초기화
├── models/                # 데이터 모델
│   ├── __init__.py
│   └── base.py           # 베이스 모델
├── schemas/              # 요청/응답 스키마
│   ├── __init__.py
│   ├── health.py
│   └── user.py
├── controllers/          # 컨트롤러 (라우트 핸들러)
│   ├── __init__.py
│   ├── health_controller.py
│   ├── user_controller.py
│   └── websocket_controller.py
├── services/            # 비즈니스 로직
│   ├── __init__.py
│   ├── health_service.py
│   ├── user_service.py
│   ├── websocket_service.py
│   └── llm_service.py
├── routes/              # 라우터 정의
│   └── __init__.py
├── middleware/          # 미들웨어
│   ├── __init__.py
│   ├── cors_middleware.py
│   ├── auth_middleware.py
│   └── logging_middleware.py
├── config/              # 설정
│   └── __init__.py
├── requirements.txt
└── README.md
```

## 설치

```bash
pip install -r requirements.txt
```

## 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
SERVER_PORT=8000
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

**주의**: `.env` 파일은 Git에 커밋되지 않습니다 (`.gitignore`에 포함됨).

## 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

또는 Python 모듈로 실행:

```bash
python -m app.main
```

## API 엔드포인트

서버 실행 후 `http://localhost:8000/docs`에서 Swagger UI를 통해 API를 테스트할 수 있습니다.

### 헬스 체크
- `GET /api/v1/health` - 서버 상태 확인

### 사용자 API
- `POST /api/v1/users` - 사용자 생성
- `GET /api/v1/users` - 모든 사용자 조회
- `GET /api/v1/users/{user_id}` - 사용자 조회
- `PUT /api/v1/users/{user_id}` - 사용자 업데이트
- `DELETE /api/v1/users/{user_id}` - 사용자 삭제

### WebSocket API
- `WS /ws` - WebSocket 연결 (OpenAI LLM 채팅)
- `WS /ws/{client_id}` - 클라이언트 ID를 받는 WebSocket 연결

**WebSocket 채팅 기능:**
- OpenAI GPT 모델을 사용한 실시간 채팅
- 대화 히스토리 유지 (최근 10턴)
- 연결별 독립적인 대화 세션

## 예시 요청

### 사용자 생성
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "홍길동", "email": "hong@example.com", "age": 30}'
```

### 사용자 조회
```bash
curl "http://localhost:8000/api/v1/users"
```

### WebSocket 연결
```javascript
// 브라우저 콘솔 또는 JavaScript 클라이언트
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => {
    console.log('WebSocket 연결됨');
    ws.send('안녕하세요!');
};
ws.onmessage = (event) => {
    console.log('받은 메시지:', event.data);
};
ws.onerror = (error) => {
    console.error('WebSocket 오류:', error);
};
ws.onclose = () => {
    console.log('WebSocket 연결 종료');
};
```

## 구조 설명

- **Models**: 데이터베이스 모델 및 베이스 클래스
- **Schemas**: Pydantic 모델 (요청/응답 검증)
- **Controllers**: API 엔드포인트 정의 (FastAPI 라우터)
- **Services**: 비즈니스 로직 처리
  - **LLM Service**: OpenAI GPT 모델을 사용한 채팅 응답 생성
  - **WebSocket Service**: WebSocket 연결 관리 및 메시지 처리
- **Routes**: 라우터 통합 및 등록
- **Middleware**: 요청/응답 처리 미들웨어
  - **CORS**: Cross-Origin Resource Sharing 설정
  - **Auth**: 인증 미들웨어 (추후 확장용)
  - **Logging**: 요청/응답 로깅

## LLM 채팅 기능

WebSocket을 통해 OpenAI GPT 모델과 실시간 채팅을 할 수 있습니다:

- **모델**: 기본적으로 `gpt-4o-mini` 사용 (변경 가능)
- **대화 히스토리**: 연결별로 독립적인 대화 세션 유지
- **히스토리 관리**: 최근 10턴(20개 메시지)만 유지하여 토큰 효율성 향상

## 미들웨어

미들웨어는 `app/main.py`에서 등록되며, 등록 순서에 따라 실행됩니다:

1. **로깅 미들웨어**: 모든 요청/응답 로깅 (디버그 모드)
2. **CORS 미들웨어**: Cross-Origin 요청 허용
3. **인증 미들웨어**: JWT 토큰 검증 등 (필요 시 활성화)

이 구조를 따라 새로운 API를 추가할 수 있습니다.

