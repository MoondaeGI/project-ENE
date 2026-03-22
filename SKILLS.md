# Skills & Slash Commands

이 프로젝트에서 사용할 수 있는 Claude Code 슬래시 커맨드 목록입니다.
모든 커맨드 정의는 `.claude/commands/` 에 있습니다.

## 구현 워크플로우

| 커맨드 | 설명 | 사용 예 |
|--------|------|---------|
| `/check-requirements <번호\|키워드>` | 요구사항 및 설계 명세 확인 | `/check-requirements memory` |
| `/implement-task <번호>` | tasks.md 기반 태스크 구현 | `/implement-task 2.1` |
| `/test-feature <경로\|함수명>` | 테스트 코드 작성 및 실행 | `/test-feature MemoryService` |
| `/memory-pattern` | Memory Stream 핵심 코드 패턴 참조 | `/memory-pattern` |

## 문서 & 동기화

| 커맨드 | 설명 | 사용 예 |
|--------|------|---------|
| `/obsidian-sync` | `.claude/docs/` → Obsidian vault 동기화 | `/obsidian-sync` |
| `/obsidian-sync <파일>` | 특정 문서만 동기화 | `/obsidian-sync design/02_agents` |

## 권장 추가 커맨드 (미구현)

아래 커맨드가 있으면 유용합니다. 필요 시 추가 요청하세요.

| 커맨드 | 설명 |
|--------|------|
| `/check-arch` | 의존성 방향(`api → workflow → services → database`) 위반 검사 |
| `/new-provider <이름>` | LLM Provider 플러그인 스캐폴드 자동 생성 |
| `/db-migrate <설명>` | Alembic 마이그레이션 생성 + 적용 + 검증 |
| `/memory-trace <memory_id>` | 기억 객체 생애주기(Message → Portrait) 추적 디버그 |

## 자동화 Hooks

파일 수정 시 자동으로 동작을 트리거하려면 hooks를 설정하세요:

```
/update-config
```

추천 hook 구성:
- **obsidian 자동 sync**: `.claude/docs/` 내 `.md` 수정 후 → `obsidian-sync.sh` 실행
- **테스트 자동 실행**: `src/` 내 `.py` 수정 후 → 관련 unit test 자동 실행
