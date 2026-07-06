# personal-llm-wiki

개인 LLM Wiki. 자료(raw)와 그것에서 파생된 지식층(wiki)을 분리해서,
자료가 쌓일수록 연결·결정·실패 사례가 누적되도록 만든 Markdown 지식 시스템.

## 구조

```
raw/        원본. 절대 수정하지 않는다.
  inbox/    처리 대기 자료를 여기에 넣는다
  samples/  테스트용 원본 8개
wiki/       원본에서 파생된 지식층
  index.md  시작점 — 목차 + 충돌 현황
  log.md    작업 이력
  sources/  원본별 요약 (1원본 = 1페이지)
  projects/ 프로젝트 현황
  concepts/ 재사용 개념·수치
  decisions/ 결정 기록
  errors/   실패 사례와 재발 방지책
  syntheses/ 재사용 가치 있는 질의 결과
tests/      평가 케이스(evals.md)와 결과(test-results.md)
.claude/skills/  wiki-ingest, wiki-query, wiki-lint
```

## 사용법

1. **자료 넣기**: 파일 1개를 `raw/inbox/`에 넣고 "wiki-ingest 실행" 요청
2. **질문하기**: 그냥 질문하면 wiki-query 절차로 답변 (출처 포함)
3. **점검하기**: 주기적으로 "wiki-lint 실행" — 수정 없이 문제만 보고

운영 규칙 전체는 [CLAUDE.md](CLAUDE.md) 참고.

## 여러 PC에서 쓰기

동기화 수단은 git(GitHub origin)이다.

1. 다른 PC 최초 1회: `git clone https://github.com/shopwaveglobal-cpu/stock.git` 후 이 폴더를 Obsidian 볼트로 열기
2. **작업 시작 전 `git pull`, 끝나면 커밋 + push** — 두 PC 동시 수정 금지
3. 주의: `raw/inbox/PORTFOLIO_LOGIC_FULL.md`(내부 전용 실수치)는 .gitignore로 제외되어 git으로 안 넘어감 — 필요하면 직접 복사
4. 인입 규칙은 어느 PC에서든 동일: raw/inbox/에 1개 → wiki-ingest

## Obsidian에서 열기

1. Obsidian → 좌하단 볼트 아이콘 → **"Open folder as vault"** → 이 폴더(`personal-llm-wiki`) 선택
2. 링크 설정은 `.obsidian/app.json`에 미리 맞춰둠 (일반 Markdown 상대 링크 — Claude가 만드는 링크와 동일 형식)
3. 주의: Obsidian에서 파일을 **이동·이름 변경하지 않는다** (링크가 깨지고 raw/ 불변 규칙과 충돌). 읽기·그래프 뷰·검색 용도로 사용하고, 내용 추가·수정은 wiki-ingest 절차로

