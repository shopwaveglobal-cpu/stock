# Wiki Index

시작점. 질의는 여기서부터 탐색한다. 작업 이력은 [log.md](log.md). 마지막 갱신: 2026-07-06

> **샘플 은퇴 (2026-07-05)**: 초기 구조 검증용 가상 데이터에서 파생된 wiki 페이지는 전부 제거됨.
> raw/samples/의 원본 8개는 보존하되(테스트 원본 표시 있음) **신규 지식 생성에 사용하지 않는다.**
> 현재 wiki/의 모든 페이지는 실제 기록 기반이다.

## 충돌 현황

| # | 항목 | 값 A | 값 B | 상태 | 기록 위치 |
|---|---|---|---|---|---|
| 1 | KRX 알림 유니버스 (가상) | 200종목 | 250종목 | 종결 — 가상 샘플 간 충돌, 샘플 은퇴 | raw/samples/ 참조 |
| 2 | 실시간 모니터 안정화 방식 | watchdog 보완 (가상 샘플) | 단일 supervisor (실제) | 종결 — 실제 기록 채택, 샘플 은퇴 | [decisions/2026-06-13-single-supervisor](decisions/2026-06-13-single-supervisor.md) |
| 3 | 실시간 모니터의 실체 | 거래대금 급증 알림 (가상 샘플) | S1·S12 매수선 모니터 (실제) | 종결 — 실제 기록 채택, 샘플 은퇴 | [sources/portfolio-logic-full](sources/portfolio-logic-full.md) |
| 4 | stockcalc 실체 | vanilla JS 웹앱 (가상 샘플) | C# WinForms v2.9 + iOS 포팅 (실제) | 종결 — 실제 기록 채택, 샘플 은퇴 | [sources/2026-06-10-stockcalc-ios-appstore](sources/2026-06-10-stockcalc-ios-appstore.md) |
| 5 | OMG 모니터링 구성 | Envelope 10분 + 업비트 1시간, omg 내 (가이드, ~2025-11-02) | crypto_realtime_monitor 5분 주기 + daily_update 00:00 분리 (분리 보고서 2025-11-07, 최신) | **부분 해소** — OMG 자체 구성은 확정(하트비트로 가동 실증, 2026-07-06). CoinRedS·Upbit1515 위치만 미확인(이 PC 전체 수색 결과 없음 — 다른 PC 또는 폐기 추정) | [sources/2025-11-07-omg-separation-summary](sources/2025-11-07-omg-separation-summary.md) |

## projects

- [stock-automation](projects/stock-automation.md) — S1·S12·OMG·Taesan 실제 시스템 현황·이력
- [local-first-apps](projects/local-first-apps.md) — StockCal(WinForms→iOS), 1IM Video Tool
- [korea-stocks-notion-template](projects/korea-stocks-notion-template.md) — 판매용 노션 거래일지 템플릿 (원타임+구독)
- (AI Tools & Content 영역은 실제 자료 인입 시 페이지 생성)

## concepts

- [windows-automation-pitfalls](concepts/windows-automation-pitfalls.md) — pythonw 금지, ps1 BOM, 재시작 진입점 1개 등 실전 함정
- [krx-tick-size](concepts/krx-tick-size.md) — 한국 주식 호가 단위 표 (공개 정보)
- [dynamic-polling-interval](concepts/dynamic-polling-interval.md) — 거리 기반 동적 폴링 주기 (OMG 제안 + S12 실운영)

## decisions

- [2026-06-10 StockCal iOS: StockCalcKit 공유 패키지](decisions/2026-06-10-stockcalc-ios-port.md)
- [2026-06-13 S1/S12 단일 supervisor 전환](decisions/2026-06-13-single-supervisor.md)
- [2025-11 OMG: WebSocket 대신 폴링 유지](decisions/2025-11-omg-polling-over-websocket.md) — 재검증 필요 표시
- [2026-06-17 노션 템플릿: 사용자 데이터 보호 원칙](decisions/2026-06-17-notion-template-user-data-protection.md)

## errors

- [2026-06-13 재시작 루프 누적 장애](errors/2026-06-13-restart-loop-accumulation.md) — 규칙: 재시작 진입점은 시스템당 1개
- [2025-11-07 OMG 일일 업데이트 중복 실행](errors/2025-11-07-omg-duplicate-daily-update.md) — 같은 "다중 진입점" 패턴의 선행 사례

## sources (원본별 요약)

- [2026-06-13 S1/S12 supervisor 전환 — 실제 기록 1호](sources/2026-06-13-s1-s12-monitor-supervisor.md)
- [전체 프로젝트 로직 총람 — ⚠ 내부 전용](sources/portfolio-logic-full.md) — 실수치는 raw 원본만 참조
- [2026-06-10 StockCal iOS 포팅 계획](sources/2026-06-10-stockcalc-ios-appstore.md)
- [2025-11 OMG 실시간 모니터링 가이드 — 오래된 문서 표시](sources/2025-11-02-omg-realtime-monitoring-guide.md)
- [2025-11-07 OMG 업데이트/모니터링 분리 보고서](sources/2025-11-07-omg-separation-summary.md)
- [2026-06-17 한국 주식 노션 템플릿 설계서](sources/2026-06-17-korea-stocks-notion-template-design.md)

## syntheses

- (아직 없음)
