# error — 재시작 루프 누적으로 알람 장애 (S1/S12)

- 발생 인지: 2026-06-08경 (PID 22816을 며칠째 못 죽임) / 해결: 2026-06-13 / 상태: 해결
- 출처: raw/inbox/2026-06-13-s1-s12-monitor-supervisor.md (실제 기록)

## 증상

- 5초마다 python 프로세스가 계속 생성되며 락 충돌 ERROR 스팸
- 기존 python 프로세스(예: PID 22816)가 WMI Terminate로 죽지 않음

## 원인 (근본)

- 진입점 4개(daily_restart_7h / smart_restart / watchdog 15분 / run_real_time_monitor)가 **각자** `S{n}_self_restart.bat` 5초 루프를 띄움
- "체크 → 비동기 VBS start" 사이의 레이스로 중복 감지 실패 → 재부팅·중복 트리거마다 루프 누적

## 조치

1. 레거시 진입점 전부 no-op 처리 (삭제 아님 — 옛 스케줄 태스크가 관리자 권한 없이는 제거 불가)
2. `monitor_supervisor.ps1` 단일 슈퍼바이저로 교체 ([decisions/2026-06-13-single-supervisor](../decisions/2026-06-13-single-supervisor.md))

## 재발 방지 규칙

- **프로세스를 띄우는 진입점은 시스템당 1개만 둔다.** 재시작 로직을 여러 스크립트에 나눠 넣지 않는다
- "체크 후 시작" 패턴은 레이스가 있다 — OS 뮤텍스 등으로 원자적으로 처리
- 삭제 권한이 없는 스케줄 태스크는 호출 대상 스크립트를 no-op로 만들어 무력화 (스크립트 삭제 금지 — 태스크가 오류를 뿜음)

## 재발 이력

- 없음 (2026-07-05 재검증: supervisor 태스크 Ready, 레거시 no-op 유지 확인)
