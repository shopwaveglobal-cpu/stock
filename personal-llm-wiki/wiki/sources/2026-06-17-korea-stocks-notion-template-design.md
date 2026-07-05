# source — 한국 주식 노션 템플릿 설계서

- 원본: raw/inbox/2026-06-17-korea-stocks-notion-template-design.md (docs/superpowers/specs/에서 복사, git 커밋 656ec835)
- 날짜: 2026-06-17 (파일명 기준) / 유형: 상품 설계서

## 요약

KOSPI·KOSDAQ 전 종목 기반 판매용 노션 거래일지 템플릿의 설계. 원타임(CSV+가이드) + 구독(주간 업데이트) 두 상품. 최상위 원칙은 **업데이트가 사용자 기록(매매일지·메모)을 절대 건드리지 않는 것**.

## 핵심 사실 (원본 기재)

- 고유키: 종목코드 6자리 (종목명은 변경되므로 병합 기준 부적합)
- 필드 2그룹 분리: 공급자 관리(시총·재무·테마 등) / 사용자 관리(매매기록·메모) — 주간 업데이트 CSV에는 사용자 필드 절대 미포함
- 1차 제외 확정: 스팩(SPAC)만. 제외분은 excluded_stocks.csv에 감사 기록. ETF·ETN·리츠·우선주·코넥스는 1차 범위 밖
- 상장폐지 종목은 삭제하지 않고 상태 표시만 (사용자 기록 보존)
- CSV는 utf-8-sig(BOM) 저장 — 한글 깨짐 방지
- 1차 업데이트는 CSV 수동 병합, 2차에 Notion API 자동화

## 관계 (해석)

- PORTFOLIO 총람의 같은 항목에는 "판매용 v2 CSV, 매매주의사유 판정(관리종목·시총 등)"이 등장 — 설계(2026-06-17) 이후 구현이 확장된 것으로 보인다. 직접 충돌 아님 ([sources/portfolio-logic-full](portfolio-logic-full.md))

## 연결

- [decisions/2026-06-17-notion-template-user-data-protection](../decisions/2026-06-17-notion-template-user-data-protection.md)
- [projects/korea-stocks-notion-template](../projects/korea-stocks-notion-template.md)
- [concepts/windows-automation-pitfalls](../concepts/windows-automation-pitfalls.md) — 한글 인코딩 규칙 공유
