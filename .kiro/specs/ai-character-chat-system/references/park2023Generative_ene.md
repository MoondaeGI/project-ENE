# Generative Agents 논문 요약 및 ENE 적용 메모

## 문서 목적
이 문서는 Joon Sung Park 외의 *Generative Agents: Interactive Simulacra of Human Behavior* 논문을 ENE 프로젝트 관점에서 재해석한 요약이다. 단순 논문 요약이 아니라, ENE의 현재 구조와 로드맵에 맞춰 **무엇을 바로 구현할지**, **어떤 테이블/파이프라인이 필요한지**, **어떤 부분은 논문 그대로 가져오면 안 되는지**까지 포함한다.

---

## 한 줄 핵심
이 논문의 본질은 “LLM에게 모든 대화를 한 번에 먹이는 것”이 아니라, **관찰(observation)을 계속 저장하고, 그중 필요한 기억만 검색(retrieval)해서, 상위 해석(reflection)을 만들고, 그 해석을 바탕으로 다음 행동과 계획(planning)을 생성하는 구조**를 만드는 데 있다.

ENE 관점에서 보면 이 논문은 단순 챗봇 설계가 아니라, **message -> memory selection -> reflection -> episode/plan -> next response** 흐름을 설계하는 기준점이다.

---

## 논문 핵심 요약

### 1. 왜 이 구조가 필요한가
논문은 LLM 단독만으로는 장기 일관성을 유지하기 어렵다고 본다. 인간처럼 보이는 agent를 만들려면 현재 상황만 잘 말하는 것이 아니라,

- 과거 경험을 기억하고
- 필요한 기억만 꺼내고
- 그 기억을 일반화해서 상위 의미를 만들고
- 그 의미를 이용해 다음 행동을 계획해야 한다.

즉, “지금 잘 대답하는 모델”이 아니라 “시간이 지나도 캐릭터성과 맥락이 유지되는 구조”가 핵심이다.

### 2. 아키텍처의 3축
논문은 agent architecture를 세 축으로 설명한다.

#### A. Memory Stream
모든 경험을 자연어 형태의 memory object로 쌓는다.
각 memory는 대략 이런 속성을 가진다.

- 자연어 설명
- 생성 시각
- 최근 접근 시각
- 중요도(importance)

가장 기본 단위는 observation이다. 예를 들면 “A가 카페에서 공부 중”, “냉장고가 비어 있음”, “B와 발렌타인 파티를 의논함” 같은 식이다.

#### B. Retrieval
모든 기억을 프롬프트에 넣지 않고, 현재 상황에 맞는 기억만 뽑는다. 논문은 retrieval score를 아래 세 요소의 가중합으로 계산한다.

- recency: 최근에 접근한 기억일수록 점수 증가
- importance: 중요한 사건일수록 점수 증가
- relevance: 현재 질문/상황과 의미적으로 비슷할수록 점수 증가

이 구조 덕분에 단순 최근 대화 몇 개가 아니라, 오래전 기억이라도 지금과 관련 있으면 다시 살아난다.

#### C. Reflection
원시 observation만 많으면 agent는 일반화와 추론이 약하다. 그래서 일정량 이상의 중요한 기억이 쌓이면, 최근 기억들로부터 상위 질문을 만들고, 그 질문에 대한 insight를 생성해 reflection으로 저장한다.

예를 들어,

- “Klaus는 연구에 오래 몰입했다”
- “Maria도 자기 연구를 열심히 하고 있다”

같은 observation이 반복되면,

- “Klaus는 연구 지향적이다”
- “Klaus와 Maria는 연구라는 공통 관심사가 있다”

같은 higher-level reflection이 생성된다.

reflection은 다시 retrieval 대상이 되므로, agent는 단순 사건 나열이 아니라 자기/타인에 대한 해석을 행동에 반영할 수 있다.

### 3. Planning
논문에서 planning은 “답변 생성”보다 넓다. agent는 하루 계획처럼 상위 플랜을 먼저 만들고, 그걸 시간 단위/행동 단위로 점차 세분화한다.

- broad plan
- hour-level plan
- 5~15분 단위 세부 행동

그리고 새로운 상황이 들어오면 기존 plan을 그대로 밀지 않고, 반응할지 말지 판단한 뒤 re-plan 한다.

즉 planning은 고정 스케줄이 아니라, **기억 + 현재 상황 + 성격 요약**을 바탕으로 계속 수정되는 미래 행동 구조다.

### 4. 평가 결과
논문은 full architecture가 memory/reflection/planning 일부를 제거한 ablation보다 더 believable하다고 보고한다. 즉,

- observation 없이
- reflection 없이
- planning 없이

그냥 LLM만 쓰는 구조보다, 이 세 층이 있을 때 캐릭터 일관성과 사회적 상호작용이 더 자연스러웠다.

다만 오류도 분명했다.

- 관련 기억 retrieval 실패
- 기억 embellishment / hallucination
- 지나치게 정중한 말투
- 환경 규칙 오해

즉 구조는 강하지만, retrieval 품질과 memory hygiene가 아주 중요하다는 뜻이다.

---

## 1. ENE에 바로 가져와야 할 핵심 개념

### A. message를 단순 대화 로그가 아니라 observation stream으로 취급
지금 message는 사람/AI 발화를 저장하는 로그다. 그런데 논문 관점에서는 이걸 “그때 agent가 경험한 사건”으로 바꿔 해석해야 한다.

즉 ENE에서 observation은 꼭 원문 message와 1:1일 필요가 없다.
예를 들면 다음처럼 정규화된 observation을 따로 만들 수 있다.

- 사용자가 Cursor automations 가격을 물어봄
- 사용자가 local markdown 기반 지식 저장에 관심을 보임
- 사용자가 개인용 vector DB + S3 백업 아이디어를 언급함
- ENE가 episode 생성 타이밍 문제를 설명함

이런 식의 **eventized memory**가 retrieval 효율을 훨씬 높인다.

즉 message는 원본, observation은 검색 친화적 재표현이 되는 쪽이 좋다.

### B. reflection은 “요약”이 아니라 “추론된 상위 의미”여야 함
현재 reflection이 10메시지마다 생성된다면, 그 reflection이 단순 대화 요약이면 논문식 reflection과는 다르다.

논문에서 reflection의 핵심은 이런 것이다.

- 반복된 행동 패턴 추출
- 사용자 선호 일반화
- 관계/감정/목표 추론
- 앞으로 영향을 줄 상위 진술 생성

ENE라면 이런 reflection이 더 맞다.

- 사용자는 단순 정보 응답보다 구조 설계를 선호한다
- 사용자는 장기 기억 구조에서 episode completeness를 중요하게 본다
- 사용자는 실무 적용 가능성과 DB 구조 정합성을 자주 검토한다
- 사용자는 아이디어가 떠오르면 즉시 로드맵/테이블 설계까지 연결하려는 편이다

이런 reflection이 retrieval에 들어가야 다음 답변이 더 ENE답고, 더 개인화된다.

### C. episode는 reflection의 상위 저장소이자 retrieval anchor가 되어야 함
논문에는 episode 테이블이 직접 나오진 않지만, ENE에는 오히려 episode가 매우 중요하다.

message는 너무 작고, reflection은 너무 추상적일 수 있다. episode는 그 사이에서 “의미 있는 사건 묶음” 역할을 해야 한다.

추천 역할은 이렇다.

- 여러 message를 하나의 사건 단위로 묶음
- 그 사건의 목적, 전환점, 결론, 감정 변화, 중요도 저장
- reflection 생성의 입력 단위가 됨
- 이후 retrieval에서 message보다 먼저 조회될 수 있는 압축 기억이 됨

즉 ENE의 retrieval 우선순위를 단순히 recent messages로 두지 말고,

**episode -> reflection -> raw message**

혹은 상황에 따라

**recent message + relevant episode + relevant reflection**

조합으로 가는 게 좋다.

### D. planning은 지금 당장 “행동 AI”까지 안 가도, response planning부터 넣을 수 있음
논문은 하루 계획, 행동 계획까지 가지만 ENE는 지금 대화 agent라서 그대로 복제할 필요는 없다. 대신 planning을 축소해서 이런 형태로 먼저 도입할 수 있다.

- 이번 대화에서 사용자와 어떤 목표를 끝낼지
- 다음 응답의 역할이 설명인지, 설계인지, 위로인지, 의사결정 보조인지
- 사용자가 지금 이어가려는 장기 작업이 무엇인지
- 지금 답변 이후 어떤 follow-up state를 남겨야 하는지

즉 ENE planning은 초기에는 physical action plan이 아니라 **dialogue intention plan**으로 시작하는 게 맞다.

예시:

- 현재 목표: episode 설계 논의 완료
- 하위 목표: trigger 기준, ongoing/finish 상태, reflection과의 연결 제안
- 응답 스타일 계획: 짧은 확답 -> 구조 제안 -> DB 영향 설명
- 종료 후 남길 상태: 사용자는 episode 완료 판정 기준을 고민 중

이건 나중에 멀티 에이전트 구조나 행동 결정 AI로 확장하기 좋다.

---

## 2. ENE DB 구조에 대한 적용 제안
현재 DDL에는 person, message, reflection, last_reflected_id, episode, tag, 그리고 tag 매핑 테이블이 있다.
이 구조는 출발점으로 괜찮지만, 논문식 구조를 살리려면 몇 개가 더 필요하다.

### 현재 구조에서 좋은 점

- message / reflection / episode 분리 방향이 좋다
- tag를 별도 테이블로 둬서 retrieval 보조가 가능하다
- important 컬럼이 episode에 있어 importance 개념을 반영할 여지가 있다
