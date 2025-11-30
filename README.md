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
│   └── websocket_service.py
├── routes/              # 라우터 정의
│   └── __init__.py
├── config/              # 설정
│   └── __init__.py
├── main.py              # 애플리케이션 진입점
├── requirements.txt
└── README.md
```

## 설치

```bash
pip install -r requirements.txt
```

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
- `WS /ws` - WebSocket 연결 (에코 서버)
- `WS /ws/{client_id}` - 클라이언트 ID를 받는 WebSocket 연결

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
- **Routes**: 라우터 통합 및 등록

이 구조를 따라 새로운 API를 추가할 수 있습니다.

