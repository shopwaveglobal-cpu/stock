# decision — S1/S12 모니터: 다중 재시작 스크립트 대신 단일 supervisor

- 날짜: 2026-06-13 / 상태: 유효 (2026-07-05 동작 재확인)
- 출처: raw/inbox/2026-06-13-s1-s12-monitor-supervisor.md (실제 기록)

## 배경

재시작 루프 누적 장애 ([errors/2026-06-13-restart-loop-accumulation](../errors/2026-06-13-restart-loop-accumulation.md)). 진입점 4개가 각자 모니터를 살리려다 서로 충돌.

## 결정과 근거

- **`S12/monitor_supervisor.ps1` 단일 슈퍼바이저 + `S1_Supervisor`/`S12_Supervisor` 태스크(1분 주기)로 통합**
- 불변식 "모니터 python 정확히 1개": 0이면 시작, 2개 이상이면 락 보유자만 남김
- OS 뮤텍스로 레이스 차단, 07시 1회 토큰 위생 재시작, 무동작 시 로그 미기록

## 관련 참고

- 과거 가상 샘플이 "watchdog 보완" 방식을 기록했으나 실제로는 watchdog 방식이 장애 원인 → index 충돌 현황 #2 (종결, 샘플 은퇴)

## 롤백

- 레거시 스크립트는 no-op 처리만 했으므로 git 이력에서 내용 복원 가능. 단, 루프 누적 재발 위험이 있으므로 롤백 전 이 결정의 배경을 반드시 확인
