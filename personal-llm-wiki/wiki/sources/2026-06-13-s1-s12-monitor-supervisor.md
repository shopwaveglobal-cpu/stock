# source — S1/S12 실시간 모니터 supervisor 전환 기록 (실제 기록 1호)

- 원본: raw/inbox/2026-06-13-s1-s12-monitor-supervisor.md (세션 메모리에서 복사한 실제 운영 기록)
- 날짜: 2026-06-13 / 유형: 오류 해결 + 결정 + 운영 주의사항
- **주의: 이 문서부터 실제 기록. raw/samples/의 8개는 테스트용 가상 데이터**

## 요약

S1/S12 실시간 모니터의 알람 장애 근본 원인(재시작 루프 누적)을 찾아, 진입점 4개를 전부 no-op 처리하고 `S12/monitor_supervisor.ps1` 단일 슈퍼바이저(1분 주기, "python 정확히 1개" 불변식)로 교체. 2026-06-13 자동 재기동 검증 완료.

## 핵심 사실 (원본 기재)

- 관리 주체: `S12/monitor_supervisor.ps1` + 스케줄 태스크 `S1_Supervisor`/`S12_Supervisor` (1분 주기)
- 불변식: 모니터 python 정확히 1개 (0이면 시작, 2+면 락 보유자만 남김, OS 뮤텍스, 07시 1회 재시작)
- no-op 처리된 레거시: `S1/S12_self_restart.bat`, `daily_restart_7h.bat`, `S1/S12_smart_restart.ps1`, `watchdog_monitors.ps1`의 S1/S12 블록
- 함정: pythonw.exe 즉시 크래시(sys.stdout=None), .ps1은 UTF-8 BOM 필수, 옛 태스크 삭제는 관리자 권한 필요
- 검증: 2026-06-13, python 강제 종료 후 ~1분 내 자동 재기동 확인

## 2026-07-05 재검증 (인입 시 확인)

- [S1/S1_self_restart.bat](../../../S1/S1_self_restart.bat) 헤더에 "DEPRECATED 2026-06-13, no-op" 확인 — 사실
- [S12/monitor_supervisor.ps1](../../../S12/monitor_supervisor.ps1) 34행에 pythonw 크래시 사유 주석 실재 — 사실
- schtasks 조회: `S1_Supervisor`/`S12_Supervisor` Ready 상태로 실행 중 — 사실
- **추가 발견 (원본에 없음)**: `S12_Monitor_Watchdog` 태스크가 3중 등록되어 있음 (schtasks 조회, 2026-07-05). 스크립트가 no-op라 실해는 없으나 관리자 권한 확보 시 정리 대상

## 연결

- [errors/2026-06-13-restart-loop-accumulation](../errors/2026-06-13-restart-loop-accumulation.md)
- [decisions/2026-06-13-single-supervisor](../decisions/2026-06-13-single-supervisor.md)
- [concepts/windows-automation-pitfalls](../concepts/windows-automation-pitfalls.md)
- [projects/stock-automation](../projects/stock-automation.md)
