# source — OMG 일일 업데이트/실시간 모니터링 분리 작업 보고서

- 원본: raw/inbox/2025-11-07-omg-separation-summary.md (omg/SEPARATION_SUMMARY.md에서 복사)
- 날짜: 2025-11-07 (원본 명시) / 유형: 작업 보고서 (문제-해결-롤백 포함)

## 요약

crypto_realtime_monitor.py에 혼재돼 있던 00:00 일일 업데이트와 실시간 모니터링을 분리. 원인은 같은 작업이 00:00(내부 스케줄러)과 00:10(배치 파일)에 2번 실행되던 중복 구조. daily_update.py를 신설하고 모니터는 00:05 재로드 + 5분 간격 모니터링만 담당.

## 핵심 사실 (원본 기재)

- 분리 후 구조: `daily_update.py`(00:00, run_daily_analysis.bat이 호출) / `crypto_realtime_monitor.py`(00:05 재로드 + **5분 간격** 모니터링)
- 백업 파일 2개 생성 후 작업 (롤백 절차 원본에 명시)
- 원본 작성 시점에 "실제 실행 테스트"는 미완 체크 상태였음

## 2026-07-06 검증 (인입 시 확인)

- `omg/monitor_heartbeat.json`: last_cycle 2026-07-06T01:17, coin_count 40 — **모니터 현재 가동 중** (사실)
- 이 문서(2025-11-07)가 가이드(~2025-11-02)보다 최신이며 현재 코드 구조와 일치 → 충돌 #5의 OMG 부분 해소 근거

## 연결

- [errors/2025-11-07-omg-duplicate-daily-update](../errors/2025-11-07-omg-duplicate-daily-update.md)
- [concepts/windows-automation-pitfalls](../concepts/windows-automation-pitfalls.md) — "진입점 1개" 규칙의 선행 사례
- [sources/2025-11-02-omg-realtime-monitoring-guide](2025-11-02-omg-realtime-monitoring-guide.md)
