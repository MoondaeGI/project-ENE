# AWS Cloud Architecture

단일 WebSocket Gateway, 2개의 ECS 서비스(WebSocket + Background Worker), RDS PostgreSQL + pgvector, S3, CloudWatch 기반의 심플한 구조입니다.

## High-Level Architecture

```
User Clients (Web/Mobile/Desktop)
    │ HTTPS/WSS
    ▼
CloudFront (CDN)
  - SSL/TLS Termination
  - DDoS Protection (WAF)
    │
    ▼
Application Load Balancer (ALB)
  - WebSocket Support (Sticky Session)
  - Health Checks (/health)
    │
    ▼
ECS Fargate - WebSocket Service (단일 인스턴스)
  FastAPI Container
  - WebSocket Server
  - LangGraph Main Workflow
    (Autonomous Behavior → Memory Retrieval →
     Emotion Analysis → Dialogue Planning →
     Message Generation → Memory Save)
  - LLM Adapter (OpenAI / Anthropic / Google / Ollama)
  vCPU: 2-4 | Memory: 8-16 GB | Auto Scaling: 1-4 tasks
    │
    ├── RDS PostgreSQL + pgvector
    │     Multi-AZ, Read Replica 1
    │     (memory_base, message, observation,
    │      reflection, episode, user_portrait, ...)
    │
    ├── S3 (ai-chat-documents/)
    │     raw/ → 웹서칭 원본 (30일 후 Glacier)
    │     chunks/ → RAG 청크 (90일 후 삭제)
    │     metadata/ → 영구 보관
    │     archive/ → 약한 기억 (1년 후 삭제)
    │
    └── EventBridge (Scheduler)
          Memory Evolution → 매일 자정
          Portrait Update  → 매일 03:00
          Topic Analysis   → 매일 06:00
              │ Trigger
              ▼
          ECS Fargate - Background Worker
          - Memory Evolution (망각 곡선 적용)
          - Reflection 생성
          - User Portrait 업데이트
          - Topic Recommender
          - 웹서칭 문서 처리 (S3 → 청킹 → 임베딩)
          vCPU: 1-2 | Memory: 4 GB | Auto Scaling: 1-3 tasks

External LLM: OpenAI / Anthropic / Google Gemini / Ollama (Local)

Monitoring: CloudWatch Logs + Metrics + X-Ray (Tracing) + Secrets Manager
```

## ECS Services

### Service 1: WebSocket Server

- **역할**: 실시간 대화 처리
- **작업**: WebSocket 연결 관리, LangGraph 워크플로우, Memory Retrieval (벡터 검색), LLM 스트리밍
- **리소스**: 2-4 vCPU, 8-16 GB RAM
- **스케일링**: CPU 70% 기준 Auto Scaling (1-4 tasks)

### Service 2: Background Worker

- **역할**: 비동기 백그라운드 작업
- **작업**: Memory Evolution (일일), Reflection 생성 (임계값 도달 시), User Portrait 업데이트, Topic Recommender, 웹 서칭 문서 처리
- **리소스**: 1-2 vCPU, 4 GB RAM
- **스케일링**: EventBridge 트리거 기반 (1-3 tasks)

## 데이터 플로우

### 실시간 대화
```
User → CloudFront → ALB → ECS WebSocket →
LangGraph Workflow → RDS (Memory Retrieval) →
LLM API → Streaming Response → User
```

### Memory Evolution
```
EventBridge (매일 자정) → ECS Background Worker →
RDS (Memory Strength 계산 및 업데이트) →
약한 기억 아카이브 → S3 (archive/)
```

### Reflection 생성
```
대화 저장 후 importance_sum 체크 →
임계값 도달 시 Background Worker 트리거 →
LLM (Reflection 생성) → RDS (reflection 테이블) →
User Portrait 업데이트
```

## 네트워크 구성

```
VPC (10.0.0.0/16)
├── Public Subnets (10.0.1.0/24, 10.0.2.0/24)
│   ├── NAT Gateway
│   └── ALB
├── Private Subnets (10.0.10.0/24, 10.0.11.0/24)
│   └── ECS Fargate Tasks
└── Database Subnets (10.0.20.0/24, 10.0.21.0/24)
    └── RDS PostgreSQL
```

**Security Groups**:

- ALB SG: 443, 80 from 0.0.0.0/0
- ECS SG: 8000 from ALB SG only
- RDS SG: 5432 from ECS SG only

## 비용 예상 (월간, 사용자 1000명 기준)

| 서비스 | 사양 | 예상 비용 |
|--------|------|-----------|
| ECS WebSocket | 2 tasks × 2 vCPU × 8 GB | $175 |
| ECS Background | 1 task × 1 vCPU × 4 GB | $50 |
| RDS PostgreSQL | db.r6g.xlarge + 100 GB | $400 |
| S3 | 500 GB + 요청 | $50 |
| ALB | 트래픽 기준 | $30 |
| CloudFront | 트래픽 기준 | $20 |
| NAT Gateway | 데이터 전송 | $50 |
| CloudWatch | 로그 + 메트릭 | $30 |
| **LLM API** | **OpenAI + Anthropic** | **$2,000** |
| **합계** | | **$2,805** |

LLM API가 전체 비용의 71% 차지. Redis/SQS 제거로 이전 대비 월 $425 절감.

## 향후 확장 포인트

| 시점 | 추가 서비스 | 이유 |
|------|------------|------|
| 동시 사용자 100+ | Redis (ElastiCache) | 임베딩 캐싱, 세션 공유 |
| 백그라운드 작업 증가 | SQS | 작업 큐잉 및 재시도 |
| 멀티 리전 | CloudFront + Route53 | 글로벌 레이턴시 감소 |
| 팀 모니터링 | Grafana Cloud | 통합 대시보드 |

## 배포 파이프라인

```
GitHub Push →
GitHub Actions (pytest + build) →
ECR (Docker Image Push) →
ECS Task Definition Update →
Blue/Green Deployment →
Health Check → Traffic Switch
```

## 모니터링 (CloudWatch)

**주요 메트릭**: ECS CPU/Memory, RDS Connection + Slow Queries, ALB Latency, LLM API 호출 횟수 (Custom), Memory Evolution 처리 시간 (Custom)

**알람**: ECS CPU > 80%, RDS Connection > 90%, Error Rate > 5%, LLM API 비용 > 임계값

**X-Ray 추적**: LangGraph 단계별 레이턴시, LLM API 호출 시간, RDS 쿼리 성능
