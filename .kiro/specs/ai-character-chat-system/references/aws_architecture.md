# AWS Cloud Architecture: AI Character Chat System

## Architecture Overview

이 문서는 AI Character Chat System의 AWS 클라우드 배포 아키텍처를 정의합니다.
단일 WebSocket Gateway, 2개의 ECS 서비스(WebSocket + Background Worker), PostgreSQL + pgvector, S3, CloudWatch 기반의 심플한 구조입니다.

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Clients                              │
│                    (Web/Mobile/Desktop)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS/WSS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CloudFront (CDN)                              │
│              - SSL/TLS Termination                               │
│              - DDoS Protection (WAF)                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Application Load Balancer (ALB)                     │
│              - WebSocket Support (Sticky Session)                │
│              - Health Checks (/health)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│           ECS Fargate - WebSocket Service (단일 인스턴스)         │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  FastAPI Container                         │  │
│  │  - WebSocket Server                                        │  │
│  │  - LangGraph Main Workflow                                 │  │
│  │    (Autonomous Behavior → Memory Retrieval →               │  │
│  │     Emotion Analysis → Dialogue Planning →                 │  │
│  │     Policy Check → Message Generation → Memory Save)       │  │
│  │  - LLM Adapter (OpenAI / Anthropic / Google / Ollama)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  vCPU: 2-4  |  Memory: 8-16 GB  |  Auto Scaling: 1-4 tasks     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼──────────────────┐
          │                │                  │
          ▼                ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────────────┐
│ RDS PostgreSQL   │ │     S3       │ │  EventBridge (Scheduler) │
│ + pgvector       │ │              │ │                          │
│                  │ │ raw/         │ │  - Memory Evolution      │
│ - person         │ │   웹서칭 원본 │ │    (매일 자정)            │
│ - message        │ │ chunks/      │ │  - Portrait Update       │
│ - observation    │ │   RAG 청크   │ │    (매일 03:00)           │
│ - reflection     │ │ metadata/    │ │  - Topic Analysis        │
│ - episode        │ │   메타데이터  │ │    (매일 06:00)           │
│ - user_portrait  │ │              │ │                          │
│ - emotion_record │ │ Lifecycle:   │ └────────────┬─────────────┘
│ - interest       │ │ raw/ → 30일  │              │ Trigger
│ - dialogue_plan  │ │ chunks/ → 90일│             ▼
│                  │ │ metadata/ 영구│ ┌────────────────────────┐
│ Multi-AZ         │ │              │ │ ECS Fargate            │
│ Read Replica 1   │ │ Versioning ON│ │ Background Worker      │
└──────────────────┘ └──────────────┘ │                        │
                                      │ - Memory Evolution     │
                                      │   (망각 곡선 적용)      │
                                      │ - Reflection 생성      │
                                      │ - User Portrait 업데이트│
                                      │ - Topic Recommender    │
                                      │ - 웹서칭 문서 처리      │
                                      │   (S3 → 청킹 → 임베딩) │
                                      │                        │
                                      │ vCPU: 1-2 | Mem: 4 GB  │
                                      │ Auto Scaling: 1-3 tasks│
                                      └────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      External LLM Services                       │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │  OpenAI    │  │ Anthropic  │  │   Google   │  │  Ollama  │  │
│  │    API     │  │    API     │  │   Gemini   │  │ (Local)  │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Monitoring & Logging                           │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │  CloudWatch    │  │  CloudWatch    │  │    X-Ray       │    │
│  │     Logs       │  │   Metrics +    │  │  (Tracing)     │    │
│  │                │  │   Dashboard    │  │                │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐                        │
│  │    Secrets     │  │  CloudTrail    │                        │
│  │    Manager     │  │  (Audit Log)   │                        │
│  └────────────────┘  └────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

## ECS Services 상세

### Service 1: WebSocket Server
- **역할**: 실시간 대화 처리
- **주요 작업**:
  - WebSocket 연결 관리
  - LangGraph 메인 워크플로우 실행
  - Memory Retrieval (RDS 벡터 검색)
  - LLM API 호출 및 스트리밍 응답
- **리소스**: 2-4 vCPU, 8-16 GB RAM
- **스케일링**: CPU 70% 기준 Auto Scaling (1-4 tasks)

### Service 2: Background Worker
- **역할**: 비동기 백그라운드 작업
- **주요 작업**:
  - Memory Evolution (망각 곡선 적용, 일일 실행)
  - Reflection 생성 (Importance 임계값 도달 시)
  - User Portrait 업데이트
  - Topic Recommender 실행
  - 웹 서칭 문서 처리 (S3 저장 → 청킹 → 임베딩 → RDS 저장)
- **리소스**: 1-2 vCPU, 4 GB RAM
- **스케일링**: EventBridge 트리거 기반 (1-3 tasks)

## 데이터 플로우

### 1. 실시간 대화 플로우
```
User → CloudFront → ALB → ECS WebSocket →
LangGraph Workflow → RDS (Memory Retrieval) →
LLM API → Streaming Response → User
```

### 2. 웹 서칭 문서 처리 플로우
```
Topic Recommender (Background Worker) →
Web Search API → S3 (raw/) →
Chunking → S3 (chunks/) →
Embedding Service → RDS (observation table)
```

### 3. Memory Evolution 플로우
```
EventBridge (매일 자정) → ECS Background Worker →
RDS (Memory Strength 계산 및 업데이트) →
약한 기억 아카이브 → S3 (archive/)
```

### 4. Reflection 생성 플로우
```
대화 저장 후 importance_sum 체크 →
임계값 도달 시 Background Worker 트리거 →
LLM (Reflection 생성) → RDS (reflection table) →
User Portrait 업데이트
```

## 네트워크 구성

```
VPC (10.0.0.0/16)
│
├── Public Subnets (10.0.1.0/24, 10.0.2.0/24)
│   ├── NAT Gateway
│   └── ALB
│
├── Private Subnets (10.0.10.0/24, 10.0.11.0/24)
│   └── ECS Fargate Tasks (WebSocket + Background)
│
└── Database Subnets (10.0.20.0/24, 10.0.21.0/24)
    └── RDS PostgreSQL
```

**Security Groups**:
- ALB SG: 443, 80 from 0.0.0.0/0
- ECS SG: 8000 from ALB SG only
- RDS SG: 5432 from ECS SG only

## S3 버킷 구조

```
ai-chat-documents/
├── raw/                    # 웹 서칭 원본 문서
│   └── {user_id}/
│       └── {doc_id}.json
├── chunks/                 # RAG용 청크 분할 문서
│   └── {user_id}/
│       └── {doc_id}/
│           ├── chunk_001.json
│           └── chunk_002.json
├── metadata/               # 문서 메타데이터 (영구 보관)
│   └── {user_id}/
│       └── {doc_id}_meta.json
└── archive/                # 약한 기억 아카이브
    └── {user_id}/
        └── {memory_id}.json
```

**Lifecycle Policy**:
- `raw/`: 30일 후 Glacier
- `chunks/`: 90일 후 삭제
- `metadata/`: 영구 보관
- `archive/`: 1년 후 삭제

## 모니터링 (CloudWatch)

**주요 메트릭**:
- ECS CPU/Memory 사용률
- RDS Connection Count, Slow Queries
- ALB Request Count, Latency
- LLM API 호출 횟수 (Custom Metric)
- Memory Evolution 처리 시간 (Custom Metric)

**알람**:
- ECS CPU > 80%
- RDS Connection > 90%
- Error Rate > 5%
- LLM API 비용 > 임계값

**X-Ray 추적**:
- LangGraph 워크플로우 단계별 레이턴시
- LLM API 호출 시간
- RDS 쿼리 성능

**향후 Grafana 연동 (선택)**:
- Grafana Cloud 무료 플랜 사용
- CloudWatch를 데이터 소스로 연결
- 별도 서버 불필요

## 비용 예상 (월간, 사용자 1000명 기준)

| 서비스 | 사양 | 예상 비용 |
|--------|------|-----------|
| ECS Fargate (WebSocket) | 2 tasks × 2 vCPU × 8 GB | $175 |
| ECS Fargate (Background) | 1 task × 1 vCPU × 4 GB | $50 |
| RDS PostgreSQL | db.r6g.xlarge + 100 GB | $400 |
| S3 | 500 GB + 요청 | $50 |
| ALB | 트래픽 기준 | $30 |
| CloudFront | 트래픽 기준 | $20 |
| NAT Gateway | 데이터 전송 | $50 |
| CloudWatch | 로그 + 메트릭 | $30 |
| **LLM API** | **OpenAI + Anthropic** | **$2,000** |
| **합계** | | **$2,805** |

Redis, SQS 제거로 이전 대비 월 $425 절감.
LLM API가 전체 비용의 71% 차지.

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
