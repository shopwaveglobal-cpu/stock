# project — Stock Automation

한국 주식·크립토 데이터 자동화 (Python, Telegram/Slack, Windows Scheduler).

## 실제 시스템 (실수치는 raw 원본만 참조 — 내부 전용)

| 시스템 | 역할 | 출처 |
|---|---|---|
| S1 | 시가총액 기반 실시간 매수선 모니터 | [sources/portfolio-logic-full](../sources/portfolio-logic-full.md) |
| S12 | 거래대금 기반 실시간 매수선 모니터 (계산 로직 S1과 공유, S12가 소스) | 동일 |
| OMG | 크립토 사이클 엔진 (Binance/CoinGecko) | 동일 |
| Taesan Scanner | 한국 주식 스캐너 (Kiwoom), 상수는 taesan/config.py 실재 | 동일 |
| Morning Brief / NASDAQ Brief | 매크로·나스닥 카드 생성 및 발송 | 동일 |

## 실행 관리 (사실)

- S1/S12 모니터는 `S12/monitor_supervisor.ps1` + `S1_Supervisor`/`S12_Supervisor` 태스크(1분 주기)가 "python 정확히 1개" 불변식으로 관리 (출처: [sources/2026-06-13-s1-s12-monitor-supervisor](../sources/2026-06-13-s1-s12-monitor-supervisor.md))
- 알람은 평일 08:00~20:00, 주말·공휴일 "비거래일 대기"가 정상 (출처: 동일)

## 이력

| 날짜 | 내용 | 출처 |
|---|---|---|
| 2026-06-08경 | 재시작 루프 누적 장애 인지 | [errors/2026-06-13-restart-loop-accumulation](../errors/2026-06-13-restart-loop-accumulation.md) |
| 2026-06-13 | 단일 supervisor 전환 + 자동 재기동 검증 | [decisions/2026-06-13-single-supervisor](../decisions/2026-06-13-single-supervisor.md) |
| 2026-07-05 | supervisor 정상 동작 재확인, 로직 총람 인입 | [sources/portfolio-logic-full](../sources/portfolio-logic-full.md) |
| 2025-11경 | OMG 모니터링: WebSocket 검토 후 폴링 유지 결정 | [decisions/2025-11-omg-polling-over-websocket](../decisions/2025-11-omg-polling-over-websocket.md) |
| 2025-11-07 | OMG 일일 업데이트 중복 실행 해결 (업데이트/모니터링 분리) | [errors/2025-11-07-omg-duplicate-daily-update](../errors/2025-11-07-omg-duplicate-daily-update.md) |

## 열린 항목

- `S12_Monitor_Watchdog` 스케줄 태스크 3중 등록 정리 — 관리자 권한 필요 (2026-07-05 schtasks 확인, 스크립트 no-op라 실해 없음)
- CoinRedS·Upbit1515(Envelope·업비트 감시) 위치 확인 — 이 PC 전체 수색에서 없음(2026-07-06). 다른 PC 또는 폐기 여부는 사용자 확인 필요. OMG 자체 모니터는 가동 확인됨(충돌 #5 부분 해소)
