# Obsidian Sync

`.claude/docs/` 문서를 Obsidian vault로 동기화합니다.

## 사용법

```
/obsidian-sync                  # 전체 docs 동기화
/obsidian-sync design/02_agents # 특정 파일만 동기화
```

## 사전 설정

`OBSIDIAN_VAULT_PATH` 환경변수 또는 `.env` 파일에 vault 경로를 지정하세요:

```
OBSIDIAN_VAULT_PATH=C:/Users/MoonDaeGI/Documents/ObsidianVault/ai-character-chat
```

## 동기화 절차

아래 순서로 실행하세요:

### 1. 대상 파일 확인

```bash
find .claude/docs -name "*.md" | sort
```

### 2. Obsidian vault로 복사

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/ObsidianVault/ai-character-chat}"

# vault 디렉터리 구조 미러링
rsync -av --delete \
  .claude/docs/ \
  "$VAULT/specs/" \
  --include="*.md" \
  --exclude="*"
```

### 3. 문서 간 관계(링크) 정리

각 파일의 `## 참고 문서` 또는 관련 섹션을 읽고, Obsidian `[[wikilink]]` 형식으로
내부 링크를 재작성합니다.

변환 규칙:
- `[design/01_workflow.md](.claude/docs/design/01_workflow.md)` → `[[01_workflow]]`
- `[requirements.md](.claude/docs/requirements.md)` → `[[requirements]]`

### 4. 관계 메타데이터(frontmatter) 추가

각 파일 상단에 Obsidian frontmatter를 추가합니다:

```yaml
---
tags: [ai-character-chat, design]
related:
  - "[[00_overview]]"
  - "[[requirements]]"
updated: <오늘 날짜>
---
```

### 5. 변경 사항 커밋 (obsidian-git 사용 시)

```bash
cd "$VAULT"
git add -A
git commit -m "sync: .claude/docs 업데이트 $(date +%Y-%m-%d)"
git push
```

## 자동 동기화 설정

`.claude/docs/` 파일 수정 시 자동으로 sync하려면 hooks를 설정하세요:

```
/update-config
```

PostToolUse hook에 아래 조건을 추가:
- **Trigger**: Edit / Write 도구로 `.claude/docs/` 내 `.md` 파일 수정 시
- **Command**: `bash .claude/scripts/obsidian-sync.sh`

---

동기화 대상: $ARGUMENTS
