# Git 컨벤션 & 테스트 규칙

## 커밋 규칙

- 프롬프트(작업) 하나가 끝날 때마다 커밋한다 — 작업 단위를 최대한 잘게 유지
- Prefix는 `YYMMDD` 형식 날짜 (ex: `260326 Init project`)
- 동사를 앞에 배치 (ex: `260326 Change database/init.py function`)

## Push 규칙

- `master` 브랜치 직접 push **절대 금지**
- Push 시 issue에 변경점 명시 필수
- Push 조건: 사용자 명시적 요청 **또는** 기능 완성 + 테스트 통과 후
- Push 전 반드시 사용자 허락 필수 — 자동 push 금지

## 테스트 규칙

- Service layer 단위테스트 필수: 성공 케이스 1회 + 엣지 케이스 존재 시 1회
- DB 테스트는 단위테스트에서 mock 허용
