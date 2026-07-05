# project — 한국 주식 노션 템플릿 (판매 상품)

KOSPI·KOSDAQ 전 종목 노션 거래일지 템플릿. 원타임 + 구독(주간 업데이트) 두 상품 구조.

## 현재 상태 (사실)

- 설계 완료 (2026-06-17, git 커밋됨). 구현 계획 문서도 존재 (docs/superpowers/plans/)
- PORTFOLIO 총람에 "판매용 v2 CSV, 매매주의사유 판정" 언급 — 구현이 설계 이후 진전된 것으로 보임 (해석). 정확한 구현 진행도는 **기록 없음**

## 핵심 설계 (사실)

- 종목코드 고유키, 공급자/사용자 필드 분리, 스팩 1차 제외(감사 파일 유지), 삭제 금지 — [decisions/2026-06-17-notion-template-user-data-protection](../decisions/2026-06-17-notion-template-user-data-protection.md)
- 데이터 소스는 어댑터 구조 (KRX, DART, 보조 소스 교체 대비)
- CSV는 utf-8-sig — 과거 인코딩 문제 재발 방지 (원본에 "깨진 한글 인코딩 사용 금지" 명시)

## 이력

| 날짜 | 내용 | 출처 |
|---|---|---|
| 2026-06-17 | 설계서 작성·커밋 | [sources/2026-06-17-korea-stocks-notion-template-design](../sources/2026-06-17-korea-stocks-notion-template-design.md) |

## 미확인

- 구현 진행 단계, v2 CSV 생성 여부, 판매 개시 여부 — 관련 기록 인입 필요
